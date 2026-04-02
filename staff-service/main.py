from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

app = FastAPI(
    title="Staff Service",
    description="Manages hotel staff records and departments",
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
class StaffCreate(BaseModel):
    first_name: str
    last_name: str
    role: str        # manager, receptionist, housekeeper, chef, security
    department: str  # front-desk, housekeeping, kitchen, management
    email: str
    phone: str

class StaffUpdate(BaseModel):
    role: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class Staff(BaseModel):
    id: int
    first_name: str
    last_name: str
    role: str
    department: str
    email: str
    phone: str

# ---------- In-Memory Store ----------
staff_db: List[dict] = [
    {"id": 1, "first_name": "Carol", "last_name": "White", "role": "manager",
     "department": "management", "email": "carol@hotelapp.com", "phone": "+1-555-0201"},
    {"id": 2, "first_name": "David", "last_name": "Brown", "role": "receptionist",
     "department": "front-desk", "email": "david@hotelapp.com", "phone": "+1-555-0202"},
    {"id": 3, "first_name": "Eva", "last_name": "Martinez", "role": "housekeeper",
     "department": "housekeeping", "email": "eva@hotelapp.com", "phone": "+1-555-0203"},
]
next_id = 4

# ---------- Routes ----------
@app.get("/", tags=["Health"])
def health():
    return {"service": "Staff Service", "status": "running", "port": 8005}

@app.get("/staff", response_model=List[Staff], tags=["Staff"])
def get_all_staff(department: Optional[str] = None):
    """List all staff members. Filter by department using ?department=front-desk."""
    if department:
        return [s for s in staff_db if s["department"] == department]
    return staff_db

@app.post("/staff", response_model=Staff, status_code=201, tags=["Staff"])
def add_staff(staff: StaffCreate):
    """Add a new staff member."""
    global next_id
    new_staff = {"id": next_id, **staff.dict()}
    staff_db.append(new_staff)
    next_id += 1
    return new_staff

@app.get("/staff/{staff_id}", response_model=Staff, tags=["Staff"])
def get_staff_member(staff_id: int):
    """Get details of a specific staff member."""
    staff = next((s for s in staff_db if s["id"] == staff_id), None)
    if not staff:
        raise HTTPException(status_code=404, detail=f"Staff member {staff_id} not found")
    return staff

@app.put("/staff/{staff_id}", response_model=Staff, tags=["Staff"])
def update_staff(staff_id: int, updates: StaffUpdate):
    """Update staff member details."""
    staff = next((s for s in staff_db if s["id"] == staff_id), None)
    if not staff:
        raise HTTPException(status_code=404, detail=f"Staff member {staff_id} not found")
    for key, value in updates.dict(exclude_none=True).items():
        staff[key] = value
    return staff

@app.delete("/staff/{staff_id}", tags=["Staff"])
def remove_staff(staff_id: int):
    """Remove a staff member from the system."""
    global staff_db
    staff = next((s for s in staff_db if s["id"] == staff_id), None)
    if not staff:
        raise HTTPException(status_code=404, detail=f"Staff member {staff_id} not found")
    staff_db = [s for s in staff_db if s["id"] != staff_id]
    return {"message": f"Staff member {staff_id} removed successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)