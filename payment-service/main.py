from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import uvicorn

app = FastAPI(
    title="Payment Service",
    description="Handles payment processing for hotel bookings",
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
class PaymentCreate(BaseModel):
    booking_id: int
    amount: float
    payment_method: str  # cash, card, online

class PaymentUpdate(BaseModel):
    status: Optional[str] = None  # pending, completed, failed, refunded

class Payment(BaseModel):
    id: int
    booking_id: int
    amount: float
    payment_method: str
    status: str
    transaction_id: str
    created_at: str

# ---------- In-Memory Store ----------
payments_db: List[dict] = [
    {"id": 1, "booking_id": 1, "amount": 320.0, "payment_method": "card",
     "status": "completed", "transaction_id": "TXN-001-2026", "created_at": "2026-03-10T08:05:00"},
    {"id": 2, "booking_id": 2, "amount": 260.0, "payment_method": "online",
     "status": "pending", "transaction_id": "TXN-002-2026", "created_at": "2026-03-12T11:10:00"},
]
next_id = 3

# ---------- Routes ----------
@app.get("/", tags=["Health"])
def health():
    return {"service": "Payment Service", "status": "running", "port": 8004}

@app.get("/payments", response_model=List[Payment], tags=["Payments"])
def get_all_payments(status: Optional[str] = None):
    """List all payments. Filter by status using ?status=completed."""
    if status:
        return [p for p in payments_db if p["status"] == status]
    return payments_db

@app.post("/payments", response_model=Payment, status_code=201, tags=["Payments"])
def process_payment(payment: PaymentCreate):
    """Process a new payment for a booking."""
    global next_id
    transaction_id = f"TXN-{str(uuid.uuid4())[:8].upper()}"
    new_payment = {
        "id": next_id,
        **payment.dict(),
        "status": "completed",
        "transaction_id": transaction_id,
        "created_at": datetime.now().isoformat()
    }
    payments_db.append(new_payment)
    next_id += 1
    return new_payment

@app.get("/payments/{payment_id}", response_model=Payment, tags=["Payments"])
def get_payment(payment_id: int):
    """Get details of a specific payment."""
    payment = next((p for p in payments_db if p["id"] == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
    return payment

@app.put("/payments/{payment_id}", response_model=Payment, tags=["Payments"])
def update_payment_status(payment_id: int, updates: PaymentUpdate):
    """Update payment status (e.g., issue a refund)."""
    payment = next((p for p in payments_db if p["id"] == payment_id), None)
    if not payment:
        raise HTTPException(status_code=404, detail=f"Payment {payment_id} not found")
    for key, value in updates.dict(exclude_none=True).items():
        payment[key] = value
    return payment

@app.get("/payments/booking/{booking_id}", response_model=List[Payment], tags=["Payments"])
def get_payments_by_booking(booking_id: int):
    """Get all payments for a specific booking."""
    results = [p for p in payments_db if p["booking_id"] == booking_id]
    return results

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)