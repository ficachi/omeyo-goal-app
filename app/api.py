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
from datetime import date

from .ai_agent import call_gemini_api, generate_image_with_imagen
from .database import SessionLocal, engine
from .models import Base, User, Goal, Footprint
from .auth import authenticate_user, create_user, create_access_token, verify_token
from .utils import get_personalized_coach_prompt
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

class ImageGenerationRequest(BaseModel):
    prompt: str

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
    user_id: int
    action: str
    path_name: str
    path_color: str
    due_time: str
    is_completed: bool = False
    priority: int

class FootprintResponse(BaseModel):
    id: int
    user_id: int
    action: str
    path_name: str
    path_color: str
    due_time: str
    is_completed: bool
    priority: int

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
        # Get user data if token is provided
        user = None
        ocean_scores = None
        totem_profile = None
        
        if token:
            payload = verify_token(token)
            if payload and payload.get("sub"):
                user = db.query(User).filter(User.email == payload["sub"]).first()
                if user:
                    # Parse ocean_scores if available
                    if user.ocean_scores:
                        try:
                            ocean_scores = json.loads(user.ocean_scores)
                        except:
                            ocean_scores = None
                    # Build full totem_profile dict if possible
                    totem_profile = {
                        "animal": user.totem_animal,
                        "emoji": getattr(user, 'totem_emoji', None),
                        "title": user.totem_title,
                        "description": getattr(user, 'totem_description', None),
                        "motivation": getattr(user, 'totem_motivation', None)
                    }
                    # Remove keys with None values
                    totem_profile = {k: v for k, v in totem_profile.items() if v is not None}
        
        # Use personalized coach prompt if user data is available, otherwise fall back to manual selection
        if ocean_scores:
            personality_instruction = get_personalized_coach_prompt(ocean_scores, totem_profile)
            print("=== DEBUG: Using personalized prompt ===")
        else:
            # Fallback to manual personality selection
            personality_prompts = {
                "coach": "You are a motivational coach. Be encouraging, goal-oriented, and help users stay focused on their objectives. If you suggest any actionable steps, output them as a JSON array at the end of your response, wrapped in [FOOTPRINTS] and [/FOOTPRINTS] tags, like this:\n[FOOTPRINTS]\n[\n  {\"action\": \"Drink a glass of water\", \"due_time\": \"Today\"},\n  {\"action\": \"Meditate for 5 minutes\", \"due_time\": \"Tomorrow\"}\n]\n[/FOOTPRINTS]",
                "mentor": "You are a wise mentor. Provide thoughtful guidance, share insights, and help users think through their challenges. If you suggest any actionable steps, output them as a JSON array at the end of your response, wrapped in [FOOTPRINTS] and [/FOOTPRINTS] tags, like this:\n[FOOTPRINTS]\n[\n  {\"action\": \"Drink a glass of water\", \"due_time\": \"Today\"},\n  {\"action\": \"Meditate for 5 minutes\", \"due_time\": \"Tomorrow\"}\n]\n[/FOOTPRINTS]",
                "friend": "You are a supportive friend. Be warm, understanding, and provide emotional support while being encouraging. If you suggest any actionable steps, output them as a JSON array at the end of your response, wrapped in [FOOTPRINTS] and [/FOOTPRINTS] tags, like this:\n[FOOTPRINTS]\n[\n  {\"action\": \"Drink a glass of water\", \"due_time\": \"Today\"},\n  {\"action\": \"Meditate for 5 minutes\", \"due_time\": \"Tomorrow\"}\n]\n[/FOOTPRINTS]",
                "therapist": "You are an empathetic therapist. Listen carefully, validate feelings, and provide therapeutic insights and coping strategies. If you suggest any actionable steps, output them as a JSON array at the end of your response, wrapped in [FOOTPRINTS] and [/FOOTPRINTS] tags, like this:\n[FOOTPRINTS]\n[\n  {\"action\": \"Drink a glass of water\", \"due_time\": \"Today\"},\n  {\"action\": \"Meditate for 5 minutes\", \"due_time\": \"Tomorrow\"}\n]\n[/FOOTPRINTS]"
            }
            personality_instruction = personality_prompts.get(chat_data.personality, personality_prompts["coach"])
            print("=== DEBUG: Using fallback prompt ===")
        
        print(f"Personality instruction length: {len(personality_instruction)}")
        print(f"Contains [FOOTPRINTS]: {personality_instruction.find('[FOOTPRINTS]') != -1}")
        
        full_prompt = f"{personality_instruction}\n\nUser: {chat_data.message}\n\nResponse:"
        
        print("=" * 50)
        print("🔍 DEBUG: CHAT REQUEST")
        print("=" * 50)
        print(f"📝 Message: {chat_data.message}")
        print(f"🎭 Received personality: '{chat_data.personality}'")
        print(f"👤 User authenticated: {user is not None}")
        print(f"🧠 User has ocean scores: {ocean_scores is not None}")
        if user:
            print(f"🐾 User totem: {user.totem_title}")
            print(f"🐾 User totem animal: {user.totem_animal}")
        print(f"📋 Using personalized prompt: {ocean_scores is not None}")
        print("=" * 50)
        print("🤖 FULL PROMPT SENT TO AI:")
        print("-" * 30)
        print(full_prompt)
        print("-" * 30)
        print("=" * 50)
        
        response = await call_gemini_api(full_prompt)
        
        print("=== DEBUG: AI RESPONSE ===")
        print(f"AI Response: {response}")
        print("=== END DEBUG ===")

        # Extract footprints from AI response
        footprints = []
        import re
        footprints_match = re.search(r'\[FOOTPRINTS\](.*?)\[/FOOTPRINTS\]', response, re.DOTALL)
        
        if footprints_match and token:
            try:
                footprints_data = json.loads(footprints_match.group(1))
                print(f"Extracted footprints from AI response: {footprints_data}")
                
                # Get user_id from token
                payload = verify_token(token)
                if payload and payload.get("sub"):
                    user = db.query(User).filter(User.email == payload["sub"]).first()
                    if user:
                        user_id = user.id
                        
                        # Convert due_time strings to proper date format
                        from datetime import datetime, timedelta
                        
                        for fp_data in footprints_data:
                            try:
                                # Parse due_time
                                due_time_str = fp_data.get('due_time', 'Today')
                                if due_time_str.lower() == 'today':
                                    due_date = datetime.now().date()
                                elif due_time_str.lower() == 'tomorrow':
                                    due_date = (datetime.now() + timedelta(days=1)).date()
                                elif due_time_str.lower() == 'tonight':
                                    due_date = datetime.now().date()
                                else:
                                    # Try to parse as date
                                    due_date = datetime.strptime(due_time_str, "%Y-%m-%d").date()
                                
                                # Create footprint in database
                                db_footprint = Footprint(
                                    user_id=user_id,
                                    action=fp_data.get('action', ''),
                                    path_name='Personal Journey',
                                    path_color='bg-blue-100 text-blue-800',
                                    due_time=due_date,
                                    is_completed=0,
                                    priority=1
                                )
                                db.add(db_footprint)
                                db.commit()
                                db.refresh(db_footprint)
                                
                                # Add to response
                                footprints.append({
                                    "id": db_footprint.id,
                                    "user_id": user_id,
                                    "action": fp_data.get('action', ''),
                                    "path_name": 'Personal Journey',
                                    "path_color": 'bg-blue-100 text-blue-800',
                                    "due_time": due_date.strftime("%Y-%m-%d"),
                                    "is_completed": False,
                                    "priority": 1
                                })
                                
                            except Exception as e:
                                print(f"Error creating footprint: {e}")
                                continue
                                
            except json.JSONDecodeError as e:
                print(f"Error parsing footprints JSON: {e}")
                print(f"Raw footprints text: {footprints_match.group(1)}")
            except Exception as e:
                print(f"Error processing footprints: {e}")

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
        
        # Fetch the full user object (with all fields)
        user_obj = db.query(User).filter(User.email == db_user.email).first()
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
            "totem_description": getattr(user_obj, "totem_description", None),
            "totem_motivation": getattr(user_obj, "totem_motivation", None),
            "ocean_scores": ocean_scores,
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
def create_footprint(footprint: FootprintCreate, db: Session = Depends(get_db)):
    print(f"Received footprint data: {footprint}")
    print(f"Footprint type: {type(footprint)}")
    print(f"Footprint dict: {footprint.dict()}")
    
    # Convert string date to date object for database
    from datetime import datetime
    try:
        due_date = datetime.strptime(footprint.due_time, "%Y-%m-%d").date()
    except ValueError:
        # If parsing fails, use today's date as fallback
        due_date = datetime.now().date()
    
    db_footprint = Footprint(
        user_id=footprint.user_id,
        action=footprint.action,
        path_name=footprint.path_name,
        path_color=footprint.path_color,
        due_time=due_date,
        is_completed=1 if footprint.is_completed else 0,
        priority=footprint.priority
    )
    db.add(db_footprint)
    db.commit()
    db.refresh(db_footprint)
    
    # Convert database model to response format
    return FootprintResponse(
        id=db_footprint.id,
        user_id=db_footprint.user_id,
        action=db_footprint.action,
        path_name=db_footprint.path_name,
        path_color=db_footprint.path_color,
        due_time=db_footprint.due_time.strftime("%Y-%m-%d"),
        is_completed=bool(db_footprint.is_completed),
        priority=db_footprint.priority
    )

@app.get("/footprints/{user_id}", response_model=List[FootprintResponse])
def get_footprints(user_id: int, db: Session = Depends(get_db)):
    footprints = db.query(Footprint).filter(Footprint.user_id == user_id).all()
    return [
        FootprintResponse(
            id=fp.id,
            user_id=fp.user_id,
            action=fp.action,
            path_name=fp.path_name,
            path_color=fp.path_color,
            due_time=fp.due_time.strftime("%Y-%m-%d"),
            is_completed=bool(fp.is_completed),
            priority=fp.priority
        ) for fp in footprints
    ]

@app.patch("/footprints/{footprint_id}/complete", response_model=FootprintResponse)
def complete_footprint(footprint_id: int = Path(...), db: Session = Depends(get_db)):
    footprint = db.query(Footprint).filter(Footprint.id == footprint_id).first()
    if not footprint:
        raise HTTPException(status_code=404, detail="Footprint not found")
    footprint.is_completed = 1
    db.commit()
    db.refresh(footprint)
    
    return FootprintResponse(
        id=footprint.id,
        user_id=footprint.user_id,
        action=footprint.action,
        path_name=footprint.path_name,
        path_color=footprint.path_color,
        due_time=footprint.due_time.strftime("%Y-%m-%d"),
        is_completed=bool(footprint.is_completed),
        priority=footprint.priority
    )

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

@app.post("/generate-image")
async def generate_image_endpoint(request_data: ImageGenerationRequest, token: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Generates an image based on the provided prompt using Imagen.
    """
    try:
        # Optional: Verify token if image generation should be restricted to authenticated users
        if token:
            payload = verify_token(token)
            if not payload or not payload.get("sub"):
                raise HTTPException(status_code=401, detail="Invalid or expired token")

        image_output = await generate_image_with_imagen(request_data.prompt)

        if image_output.startswith("Error:"):
            raise HTTPException(status_code=500, detail=image_output)

        # Always return as {"image": ...} for frontend compatibility
        return {"image": image_output}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error in generate-image endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 