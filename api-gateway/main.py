from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, RedirectResponse
import httpx
import uvicorn
from copy import deepcopy
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Hotel Booking - API Gateway",
    description="""
## 🏨 Hotel Booking System — API Gateway

This gateway provides a **single entry point** for all microservices.
Instead of remembering 6 different ports, all requests go through **port 8000**.

### Routing Table

| Gateway Prefix         | Microservice           | Port |
|------------------------|------------------------|------|
| `/api/guests/*`        | Guest Service          | 8001 |
| `/api/rooms/*`         | Room Service           | 8002 |
| `/api/bookings/*`      | Booking Service        | 8003 |
| `/api/payments/*`      | Payment Service        | 8004 |
| `/api/staff/*`         | Staff Service          | 8005 |
| `/api/feedbacks/*`     | Feedback Service       | 8006 |
""",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:3006",
        "http://localhost:8000",
        "http://localhost:8007",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICE_REGISTRY = {
    "guests":    "http://localhost:8001",
    "rooms":     "http://localhost:8002",
    "bookings":  "http://localhost:8003",
    "payments":  "http://localhost:8004",
    "staff":     "http://localhost:8005",
    "feedbacks": "http://localhost:8006",
}


def _prefixed_ref(ref: str, service_name: str) -> str:
    if not isinstance(ref, str):
        return ref
    if ref.startswith("#/components/"):
        return ref.replace("#/components/", f"#/components/{service_name}_", 1)
    return ref


def _walk_and_prefix_refs(obj, service_name: str):
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str):
                new_dict[k] = _prefixed_ref(v, service_name)
            else:
                new_dict[k] = _walk_and_prefix_refs(v, service_name)
        return new_dict
    elif isinstance(obj, list):
        return [_walk_and_prefix_refs(v, service_name) for v in obj]
    else:
        return obj


def _merge_service_openapi(base_schema: dict, service_name: str, service_schema: dict):
    # Merge paths with /api/{service_name} prefix
    for path, path_item in service_schema.get("paths", {}).items():
        gateway_path = f"/api/{service_name}{path}"
        path_item_prefixed = _walk_and_prefix_refs(deepcopy(path_item), service_name)
        base_schema.setdefault("paths", {})[gateway_path] = path_item_prefixed

    # Merge components with service prefix to avoid collisions
    components = service_schema.get("components", {})
    base_components = base_schema.setdefault("components", {})
    for comp_type, comp_map in components.items():
        base_comp_type = base_components.setdefault(comp_type, {})
        for comp_name, comp_detail in comp_map.items():
            new_name = f"{service_name}_{comp_name}"
            base_comp_type[new_name] = _walk_and_prefix_refs(deepcopy(comp_detail), service_name)

    # Merge tags, optionally keep original service tag to avoid collisions
    for tag in service_schema.get("tags", []):
        new_tag = deepcopy(tag)
        new_tag["name"] = f"{service_name.capitalize()} - {tag.get('name', '')}"
        base_schema.setdefault("tags", []).append(new_tag)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    gateway_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Keep gateway defaults (health/service listing)
    gateway_schema.setdefault("paths", {})
    gateway_schema.setdefault("components", {})
    gateway_schema.setdefault("tags", gateway_schema.get("tags", []))

    for service_name, service_url in SERVICE_REGISTRY.items():
        try:
            r = httpx.get(f"{service_url}/openapi.json", timeout=3.0)
            r.raise_for_status()
            service_schema = r.json()
            _merge_service_openapi(gateway_schema, service_name, service_schema)
        except Exception:
            # service may be down during startup; continue with what we have
            continue

    app.openapi_schema = gateway_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/", include_in_schema=False)
def root():
    return {
        "service": "API Gateway",
        "status": "running",
        "port": 8000,
        "registered_services": list(SERVICE_REGISTRY.keys())
    }

@app.get("/ui", include_in_schema=False)
def ui_redirect():
    return RedirectResponse(url="http://localhost:8007")

@app.get("/health", tags=["Gateway"])
def gateway_health():
    return {
        "service": "API Gateway",
        "status": "running",
        "port": 8000,
        "registered_services": list(SERVICE_REGISTRY.keys())
    }

@app.get("/services", tags=["Gateway"])
def list_services():
    return {
        name: {"upstream": url, "gateway_prefix": f"/api/{name}"}
        for name, url in SERVICE_REGISTRY.items()
    }

async def proxy_request(service_name: str, path: str, request: Request) -> Response:
    if service_name not in SERVICE_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_name}' not found. Available: {list(SERVICE_REGISTRY.keys())}"
        )
    base_url = SERVICE_REGISTRY[service_name]
    upstream_path = f"/{service_name}/{path}" if path else f"/{service_name}"
    query_string = str(request.url.query)
    upstream_url = f"{base_url}{upstream_path}"
    if query_string:
        upstream_url += f"?{query_string}"
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length")
    }
    body = await request.body()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            upstream_response = await client.request(
                method=request.method,
                url=upstream_url,
                headers=headers,
                content=body,
            )
        return Response(
            content=upstream_response.content,
            status_code=upstream_response.status_code,
            media_type=upstream_response.headers.get("content-type", "application/json"),
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=f"Service '{service_name}' is unavailable. Make sure it is running."
        )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail=f"Service '{service_name}' timed out.")

@app.api_route(
    "/api/{service_name}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Gateway Proxy"]
)
async def gateway_proxy_root(service_name: str, request: Request):
    return await proxy_request(service_name, "", request)

@app.api_route(
    "/api/{service_name}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Gateway Proxy"]
)
async def gateway_proxy(service_name: str, path: str, request: Request):
    return await proxy_request(service_name, path, request)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
