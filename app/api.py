from fastapi import FastAPI, HTTPException, Depends, Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from sqlalchemy.exc import NoResultFound

from .ai_agent import call_gemini_api
from .database import SessionLocal, engine
from .models import Base, User, Goal, Footprint
from .auth import authenticate_user, create_user, create_access_token, verify_token
import json
# from .supabase_config import get_supabase_client

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

# Mount static files (commented out since static directory doesn't exist)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for API
class ChatMessage(BaseModel):
    message: str
    personality: str = "coach"

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    personality: str = None
    totem_animal: str = None
    totem_emoji: str = None
    totem_title: str = None
    ocean_scores: dict = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    personality: str = None
    totem_animal: str = None
    totem_emoji: str = None
    totem_title: str = None
    ocean_scores: dict = None

class GoalCreate(BaseModel):
    user_id: int
    description: str
    status: str = "active"

class FootprintCreate(BaseModel):
    action: str
    path_name: str
    path_color: str
    due_time: str
    is_completed: bool = False
    priority: int

class FootprintResponse(FootprintCreate):
    id: int
    user_id: int

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_root():
    """API root endpoint"""
    return {"message": "Welcome to Omeyo AI Agent API!", "version": "1.0.0"}

@app.get("/supabase-test")
async def test_supabase():
    """Test Supabase connection"""
    try:
        # For now, return a simple response since Supabase is optional
        return {
            "status": "success",
            "message": "Supabase is not configured (optional feature)",
            "supabase_url": os.getenv("SUPABASE_URL", "Not configured")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase error: {str(e)}")

@app.post("/chat")
async def chat_with_agent(chat_data: ChatMessage, token: Optional[str] = None, db: Session = Depends(get_db)):
    """Chat with the AI agent"""
    try:
        # Create a simple prompt with personality
        personality_prompts = {
            "coach": "You are a motivational coach. Be encouraging, goal-oriented, and help users stay focused on their objectives.",
            "mentor": "You are a wise mentor. Provide thoughtful guidance, share insights, and help users think through their challenges.",
            "friend": "You are a supportive friend. Be warm, understanding, and provide emotional support while being encouraging.",
            "therapist": "You are an empathetic therapist. Listen carefully, validate feelings, and provide therapeutic insights and coping strategies."
        }
        
        personality_instruction = personality_prompts.get(chat_data.personality, personality_prompts["coach"])
        full_prompt = f"{personality_instruction}\n\nUser: {chat_data.message}\n\nResponse:"
        
        response = await call_gemini_api(full_prompt)

        # --- Footprint extraction logic (placeholder) ---
        footprints = []
        if ("drink more water" in chat_data.message.lower() or "drink water" in chat_data.message.lower()) and ("yes" in chat_data.message.lower() or "sure" in chat_data.message.lower()):
            # If token is provided, get user_id
            user_id = None
            if token:
                payload = verify_token(token)
                if payload and payload.get("sub"):
                    user = db.query(User).filter(User.email == payload["sub"]).first()
                    if user:
                        user_id = user.id
            fp_obj = {
                "action": "Drink a glass of water (8oz)",
                "path_name": "Personal Journey",
                "path_color": "bg-blue-100 text-blue-800",
                "due_time": "Now",
                "is_completed": False,
                "priority": 1
            }
            if user_id:
                db_footprint = Footprint(
                    user_id=user_id,
                    **fp_obj
                )
                db.add(db_footprint)
                db.commit()
                db.refresh(db_footprint)
                fp_obj = {**fp_obj, "id": db_footprint.id, "user_id": user_id}
            else:
                fp_obj = {**fp_obj, "id": 1, "user_id": 0}
            footprints.append(fp_obj)
        # --- End placeholder ---

        return {
            "response": response,
            "personality": chat_data.personality,
            "conversation": [{"role": "user", "content": chat_data.message}, {"role": "assistant", "content": response}],
            "footprints": footprints
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Agent error: {str(e)}")

@app.post("/auth/register", response_model=dict)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        db_user = create_user(
            db=db,
            name=user.name,
            email=user.email,
            password=user.password,
            personality=user.personality,
            totem_animal=user.totem_animal,
            totem_emoji=user.totem_emoji,
            totem_title=user.totem_title,
            ocean_scores=user.ocean_scores
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": db_user.email})
        
        return {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login", response_model=dict)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user_obj = authenticate_user(db, user.email, user.password)
    if not user_obj:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user_obj.email})
    
    # Parse ocean_scores if available
    ocean_scores = None
    if user_obj.ocean_scores:
        try:
            ocean_scores = json.loads(user_obj.ocean_scores)
        except:
            pass
    
    return {
        "id": user_obj.id,
        "name": user_obj.name,
        "email": user_obj.email,
        "personality": user_obj.personality,
        "totem_animal": user_obj.totem_animal,
        "totem_emoji": user_obj.totem_emoji,
        "totem_title": user_obj.totem_title,
        "ocean_scores": ocean_scores,
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/auth/me", response_model=UserResponse)
def get_current_user(token: str, db: Session = Depends(get_db)):
    """Get current user information"""
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Parse ocean_scores if available
    ocean_scores = None
    if user.ocean_scores:
        try:
            ocean_scores = json.loads(user.ocean_scores)
        except:
            pass
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        personality=user.personality,
        totem_animal=user.totem_animal,
        totem_emoji=user.totem_emoji,
        totem_title=user.totem_title,
        ocean_scores=ocean_scores
    )

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

@app.post("/footprints/", response_model=FootprintResponse)
def create_footprint(footprint: FootprintCreate, user_id: int, db: Session = Depends(get_db)):
    db_footprint = Footprint(
        user_id=user_id,
        action=footprint.action,
        path_name=footprint.path_name,
        path_color=footprint.path_color,
        due_time=footprint.due_time,
        is_completed=1 if footprint.is_completed else 0,
        priority=footprint.priority
    )
    db.add(db_footprint)
    db.commit()
    db.refresh(db_footprint)
    return db_footprint

@app.get("/footprints/{user_id}", response_model=List[FootprintResponse])
def get_footprints(user_id: int, db: Session = Depends(get_db)):
    return db.query(Footprint).filter(Footprint.user_id == user_id).all()

@app.patch("/footprints/{footprint_id}/complete", response_model=FootprintResponse)
def complete_footprint(footprint_id: int = Path(...), db: Session = Depends(get_db)):
    footprint = db.query(Footprint).filter(Footprint.id == footprint_id).first()
    if not footprint:
        raise HTTPException(status_code=404, detail="Footprint not found")
    footprint.is_completed = 1
    db.commit()
    db.refresh(footprint)
    return footprint

@app.delete("/footprints/{footprint_id}", response_model=dict)
def delete_footprint(footprint_id: int = Path(...), db: Session = Depends(get_db)):
    footprint = db.query(Footprint).filter(Footprint.id == footprint_id).first()
    if not footprint:
        raise HTTPException(status_code=404, detail="Footprint not found")
    db.delete(footprint)
    db.commit()
    return {"detail": "Footprint deleted"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Omeyo AI Agent is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 