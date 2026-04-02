from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Guest Service",
    description="Manages hotel guest profiles and registration",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:3004", "http://localhost:3005", "http://localhost:3006", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Models ----------
class GuestCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    nationality: str

class GuestUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    nationality: Optional[str] = None

class Guest(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    nationality: str
    created_at: str

# ---------- In-Memory Store ----------
guests_db: List[dict] = [
    {"id": 1, "first_name": "Alice", "last_name": "Johnson", "email": "alice@example.com",
     "phone": "+1-555-0101", "nationality": "American", "created_at": "2026-01-10T09:00:00"},
    {"id": 2, "first_name": "Bob", "last_name": "Smith", "email": "bob@example.com",
     "phone": "+44-20-7946-0958", "nationality": "British", "created_at": "2026-01-12T10:30:00"},
]
next_id = 3

# ---------- Routes ----------
@app.get("/", tags=["Health"])
def health():
    return {"service": "Guest Service", "status": "running", "port": 8001}

@app.get("/guests", response_model=List[Guest], tags=["Guests"])
def get_all_guests():
    """Retrieve all registered guests."""
    return guests_db

@app.post("/guests", response_model=Guest, status_code=201, tags=["Guests"])
def create_guest(guest: GuestCreate):
    """Register a new guest."""
    global next_id
    new_guest = {
        "id": next_id,
        **guest.dict(),
        "created_at": datetime.now().isoformat()
    }
    guests_db.append(new_guest)
    next_id += 1
    return new_guest

@app.get("/guests/{guest_id}", response_model=Guest, tags=["Guests"])
def get_guest(guest_id: int):
    """Get a specific guest by ID."""
    guest = next((g for g in guests_db if g["id"] == guest_id), None)
    if not guest:
        raise HTTPException(status_code=404, detail=f"Guest {guest_id} not found")
    return guest

@app.put("/guests/{guest_id}", response_model=Guest, tags=["Guests"])
def update_guest(guest_id: int, updates: GuestUpdate):
    """Update guest information."""
    guest = next((g for g in guests_db if g["id"] == guest_id), None)
    if not guest:
        raise HTTPException(status_code=404, detail=f"Guest {guest_id} not found")
    for key, value in updates.dict(exclude_none=True).items():
        guest[key] = value
    return guest

@app.delete("/guests/{guest_id}", tags=["Guests"])
def delete_guest(guest_id: int):
    """Remove a guest from the system."""
    global guests_db
    guest = next((g for g in guests_db if g["id"] == guest_id), None)
    if not guest:
        raise HTTPException(status_code=404, detail=f"Guest {guest_id} not found")
    guests_db = [g for g in guests_db if g["id"] != guest_id]
    return {"message": f"Guest {guest_id} deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)