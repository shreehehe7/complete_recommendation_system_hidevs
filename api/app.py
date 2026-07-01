from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import uuid
import time
import os

from data.database import Database
from data.repositories import UserRepository, ContentRepository
from engine.orchestrator import RecommendationOrchestrator

# Setup Database and Orchestrator
DB_PATH = "recommendation.db"
# Use absolute path to ensure we find the db regardless of run directory
db_abs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), DB_PATH)
db = Database(db_abs_path)
orchestrator = RecommendationOrchestrator(db)
user_repo = UserRepository(db)
content_repo = ContentRepository(db)

app = FastAPI(
    title="Recommendation System API",
    description="API for fetching personalized content recommendations.",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request tracing and logging
@app.middleware("http")
async def add_request_id_and_log(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = str(round(process_time, 2))
    
    print(f"[{request_id}] {request.method} {request.url.path} - {response.status_code} - {process_time:.2f}ms")
    
    return response

# Pydantic models for API validation
class FeedbackRequest(BaseModel):
    user_id: int
    content_id: str
    interaction_type: str
    rating: Optional[int] = None

# API Endpoints

@app.get("/api/users")
def get_users():
    """Returns list of all users."""
    users = user_repo.get_all()
    return [{"id": u.id, "name": u.name, "interests": u.interests} for u in users]

@app.get("/api/recommend/{user_id}")
def get_recommendations(user_id: int, limit: int = 5, strategy: str = 'hybrid'):
    """Get recommendations for a user."""
    if strategy not in ['collaborative', 'content', 'hybrid']:
        raise HTTPException(status_code=400, detail="Invalid strategy. Must be 'collaborative', 'content', or 'hybrid'")
        
    recommendations, process_time = orchestrator.get_recommendations(user_id, limit, strategy)
    
    if recommendations is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
    return {
        "user_id": user_id,
        "strategy": strategy,
        "limit": limit,
        "response_time_ms": round(process_time, 2),
        "recommendations": recommendations
    }

@app.post("/api/feedback")
def record_feedback(feedback: FeedbackRequest, background_tasks: BackgroundTasks):
    """Record user interaction with content."""
    valid_types = ['view', 'click', 'rate', 'complete']
    if feedback.interaction_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid interaction_type. Must be one of {valid_types}")
        
    if feedback.interaction_type == 'rate' and (feedback.rating is None or not (1 <= feedback.rating <= 5)):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5 for 'rate' interaction")
        
    # Record asynchronously to not block the response
    background_tasks.add_task(
        orchestrator.record_feedback, 
        feedback.user_id, 
        feedback.content_id, 
        feedback.interaction_type, 
        feedback.rating
    )
    
    return {"status": "success", "message": "Feedback recorded successfully"}

@app.get("/api/health")
def health_check():
    """System health check."""
    # Check DB connection
    db_status = "ok"
    try:
        with db.get_connection() as conn:
            conn.execute("SELECT 1")
    except Exception as e:
        db_status = f"error: {str(e)}"
        
    return {
        "status": "healthy" if db_status == "ok" else "unhealthy",
        "database": db_status,
        "cache_size": len(orchestrator.cache),
        "timestamp": datetime.now().isoformat() if 'datetime' in globals() else time.time()
    }

@app.get("/api/metrics")
def get_metrics():
    """System performance metrics."""
    return orchestrator.get_metrics_report()

# Mount frontend files at the root
# Check if frontend dir exists (might be running from tests)
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
