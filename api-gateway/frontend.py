from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="Hotel Booking - Frontend")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/static/index.html")


if __name__ == "__main__":
    uvicorn.run("frontend:app", host="0.0.0.0", port=8007, reload=True)
