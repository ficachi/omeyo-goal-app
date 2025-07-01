from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from .ai_agent import AIAgent
from .database import SessionLocal, engine
from .models import Base, User, Goal

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Omeyo AI Agent", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for API
class ChatMessage(BaseModel):
    message: str
    personality: str = "coach"

class UserCreate(BaseModel):
    name: str
    personality: str

class GoalCreate(BaseModel):
    user_id: int
    description: str
    status: str = "active"

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main chat interface"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/chat")
async def chat_with_agent(chat_data: ChatMessage):
    """Chat with the AI agent"""
    try:
        agent = AIAgent(chat_data.personality)
        agent.add_user_message(chat_data.message)
        response = agent.get_response()
        
        return {
            "response": response,
            "personality": chat_data.personality,
            "conversation": agent.get_conversation()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Agent error: {str(e)}")

@app.post("/users/", response_model=dict)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    db_user = User(name=user.name, personality=user.personality)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "name": db_user.name, "personality": db_user.personality}

@app.get("/users/", response_model=List[dict])
def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).all()
    return [{"id": user.id, "name": user.name, "personality": user.personality} for user in users]

@app.post("/goals/", response_model=dict)
def create_goal(goal: GoalCreate, db: Session = Depends(get_db)):
    """Create a new goal"""
    db_goal = Goal(
        user_id=goal.user_id,
        description=goal.description,
        status=goal.status
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return {
        "id": db_goal.id,
        "user_id": db_goal.user_id,
        "description": db_goal.description,
        "status": db_goal.status
    }

@app.get("/goals/{user_id}", response_model=List[dict])
def get_user_goals(user_id: int, db: Session = Depends(get_db)):
    """Get goals for a specific user"""
    goals = db.query(Goal).filter(Goal.user_id == user_id).all()
    return [
        {
            "id": goal.id,
            "user_id": goal.user_id,
            "description": goal.description,
            "status": goal.status
        } for goal in goals
    ]

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Omeyo AI Agent is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 