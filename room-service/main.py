from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

app = FastAPI(
    title="Room Service",
    description="Manages hotel rooms, availability, and pricing",
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
class RoomCreate(BaseModel):
    room_number: str
    room_type: str  # single, double, suite, deluxe
    price_per_night: float
    floor: int
    amenities: str  # comma-separated

class RoomUpdate(BaseModel):
    room_type: Optional[str] = None
    price_per_night: Optional[float] = None
    is_available: Optional[bool] = None
    amenities: Optional[str] = None

class Room(BaseModel):
    id: int
    room_number: str
    room_type: str
    price_per_night: float
    floor: int
    is_available: bool
    amenities: str

# ---------- In-Memory Store ----------
rooms_db: List[dict] = [
    {"id": 1, "room_number": "101", "room_type": "single", "price_per_night": 80.0,
     "floor": 1, "is_available": True, "amenities": "WiFi, TV, AC"},
    {"id": 2, "room_number": "201", "room_type": "double", "price_per_night": 130.0,
     "floor": 2, "is_available": True, "amenities": "WiFi, TV, AC, Mini-bar"},
    {"id": 3, "room_number": "301", "room_type": "suite", "price_per_night": 280.0,
     "floor": 3, "is_available": False, "amenities": "WiFi, TV, AC, Jacuzzi, Balcony"},
]
next_id = 4

# ---------- Routes ----------
@app.get("/", tags=["Health"])
def health():
    return {"service": "Room Service", "status": "running", "port": 8002}

@app.get("/rooms", response_model=List[Room], tags=["Rooms"])
def get_all_rooms(available_only: bool = False):
    """List all rooms. Filter by availability using ?available_only=true."""
    if available_only:
        return [r for r in rooms_db if r["is_available"]]
    return rooms_db

@app.post("/rooms", response_model=Room, status_code=201, tags=["Rooms"])
def create_room(room: RoomCreate):
    """Add a new room to the hotel."""
    global next_id
    if any(r["room_number"] == room.room_number for r in rooms_db):
        raise HTTPException(status_code=400, detail=f"Room {room.room_number} already exists")
    new_room = {"id": next_id, **room.dict(), "is_available": True}
    rooms_db.append(new_room)
    next_id += 1
    return new_room

@app.get("/rooms/{room_id}", response_model=Room, tags=["Rooms"])
def get_room(room_id: int):
    """Get details of a specific room."""
    room = next((r for r in rooms_db if r["id"] == room_id), None)
    if not room:
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found")
    return room

@app.put("/rooms/{room_id}", response_model=Room, tags=["Rooms"])
def update_room(room_id: int, updates: RoomUpdate):
    """Update room details or availability."""
    room = next((r for r in rooms_db if r["id"] == room_id), None)
    if not room:
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found")
    for key, value in updates.dict(exclude_none=True).items():
        room[key] = value
    return room

@app.delete("/rooms/{room_id}", tags=["Rooms"])
def delete_room(room_id: int):
    """Remove a room from the system."""
    global rooms_db
    room = next((r for r in rooms_db if r["id"] == room_id), None)
    if not room:
        raise HTTPException(status_code=404, detail=f"Room {room_id} not found")
    rooms_db = [r for r in rooms_db if r["id"] != room_id]
    return {"message": f"Room {room_id} deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)