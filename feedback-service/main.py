from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Feedback Service",
    description="Collects and manages guest reviews and feedback",
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
class FeedbackCreate(BaseModel):
    guest_id: int
    booking_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 (poor) to 5 (excellent)")
    comment: str

class FeedbackUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class Feedback(BaseModel):
    id: int
    guest_id: int
    booking_id: int
    rating: int
    comment: str
    created_at: str

# ---------- In-Memory Store ----------
feedbacks_db: List[dict] = [
    {"id": 1, "guest_id": 1, "booking_id": 1, "rating": 5,
     "comment": "Excellent stay! The staff were very professional.", "created_at": "2026-04-06T10:00:00"},
    {"id": 2, "guest_id": 2, "booking_id": 2, "rating": 4,
     "comment": "Great room and clean facilities. Highly recommend.", "created_at": "2026-04-13T12:00:00"},
]
next_id = 3

# ---------- Routes ----------
@app.get("/", tags=["Health"])
def health():
    return {"service": "Feedback Service", "status": "running", "port": 8006}

@app.get("/feedbacks", response_model=List[Feedback], tags=["Feedback"])
def get_all_feedbacks(min_rating: Optional[int] = None):
    """List all feedback. Filter by minimum rating using ?min_rating=4."""
    if min_rating is not None:
        return [f for f in feedbacks_db if f["rating"] >= min_rating]
    return feedbacks_db

@app.post("/feedbacks", response_model=Feedback, status_code=201, tags=["Feedback"])
def submit_feedback(feedback: FeedbackCreate):
    """Submit new feedback for a stay."""
    global next_id
    new_feedback = {
        "id": next_id,
        **feedback.dict(),
        "created_at": datetime.now().isoformat()
    }
    feedbacks_db.append(new_feedback)
    next_id += 1
    return new_feedback

@app.get("/feedbacks/{feedback_id}", response_model=Feedback, tags=["Feedback"])
def get_feedback(feedback_id: int):
    """Get a specific feedback entry."""
    feedback = next((f for f in feedbacks_db if f["id"] == feedback_id), None)
    if not feedback:
        raise HTTPException(status_code=404, detail=f"Feedback {feedback_id} not found")
    return feedback

@app.put("/feedbacks/{feedback_id}", response_model=Feedback, tags=["Feedback"])
def update_feedback(feedback_id: int, updates: FeedbackUpdate):
    """Update a feedback entry."""
    feedback = next((f for f in feedbacks_db if f["id"] == feedback_id), None)
    if not feedback:
        raise HTTPException(status_code=404, detail=f"Feedback {feedback_id} not found")
    for key, value in updates.dict(exclude_none=True).items():
        feedback[key] = value
    return feedback

@app.delete("/feedbacks/{feedback_id}", tags=["Feedback"])
def delete_feedback(feedback_id: int):
    """Delete a feedback entry."""
    global feedbacks_db
    feedback = next((f for f in feedbacks_db if f["id"] == feedback_id), None)
    if not feedback:
        raise HTTPException(status_code=404, detail=f"Feedback {feedback_id} not found")
    feedbacks_db = [f for f in feedbacks_db if f["id"] != feedback_id]
    return {"message": f"Feedback {feedback_id} deleted successfully"}

@app.get("/feedbacks/guest/{guest_id}", response_model=List[Feedback], tags=["Feedback"])
def get_feedbacks_by_guest(guest_id: int):
    """Get all feedbacks submitted by a specific guest."""
    return [f for f in feedbacks_db if f["guest_id"] == guest_id]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8006, reload=True)