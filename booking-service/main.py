from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Booking Service",
    description="Manages hotel reservations and bookings",
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
class BookingCreate(BaseModel):
    guest_id: int
    room_id: int
    check_in_date: str   # YYYY-MM-DD
    check_out_date: str  # YYYY-MM-DD
    total_price: float

class BookingUpdate(BaseModel):
    check_in_date: Optional[str] = None
    check_out_date: Optional[str] = None
    status: Optional[str] = None  # pending, confirmed, cancelled, completed
    total_price: Optional[float] = None

class Booking(BaseModel):
    id: int
    guest_id: int
    room_id: int
    check_in_date: str
    check_out_date: str
    status: str
    total_price: float
    created_at: str

# ---------- In-Memory Store ----------
bookings_db: List[dict] = [
    {"id": 1, "guest_id": 1, "room_id": 1, "check_in_date": "2026-04-01",
     "check_out_date": "2026-04-05", "status": "confirmed", "total_price": 320.0,
     "created_at": "2026-03-10T08:00:00"},
    {"id": 2, "guest_id": 2, "room_id": 2, "check_in_date": "2026-04-10",
     "check_out_date": "2026-04-12", "status": "pending", "total_price": 260.0,
     "created_at": "2026-03-12T11:00:00"},
]
next_id = 3

# ---------- Routes ----------
@app.get("/", tags=["Health"])
def health():
    return {"service": "Booking Service", "status": "running", "port": 8003}

@app.get("/bookings", response_model=List[Booking], tags=["Bookings"])
def get_all_bookings(status: Optional[str] = None):
    """List all bookings. Filter by status using ?status=confirmed."""
    if status:
        return [b for b in bookings_db if b["status"] == status]
    return bookings_db

@app.post("/bookings", response_model=Booking, status_code=201, tags=["Bookings"])
def create_booking(booking: BookingCreate):
    """Create a new reservation."""
    global next_id
    new_booking = {
        "id": next_id,
        **booking.dict(),
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    bookings_db.append(new_booking)
    next_id += 1
    return new_booking

@app.get("/bookings/{booking_id}", response_model=Booking, tags=["Bookings"])
def get_booking(booking_id: int):
    """Get details of a specific booking."""
    booking = next((b for b in bookings_db if b["id"] == booking_id), None)
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    return booking

@app.put("/bookings/{booking_id}", response_model=Booking, tags=["Bookings"])
def update_booking(booking_id: int, updates: BookingUpdate):
    """Update booking details or status."""
    booking = next((b for b in bookings_db if b["id"] == booking_id), None)
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    for key, value in updates.dict(exclude_none=True).items():
        booking[key] = value
    return booking

@app.delete("/bookings/{booking_id}", tags=["Bookings"])
def cancel_booking(booking_id: int):
    """Cancel a booking."""
    booking = next((b for b in bookings_db if b["id"] == booking_id), None)
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    booking["status"] = "cancelled"
    return {"message": f"Booking {booking_id} cancelled successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)