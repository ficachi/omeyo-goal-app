from fastapi import FastAPI, HTTPException, Depends, Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from sqlalchemy.exc import NoResultFound
from datetime import date, datetime, timedelta

from .ai_agent import call_gemini_api, generate_image_with_imagen
from .database import SessionLocal, engine
from .models import Base, User, Goal, Footprint, Path as PathModel, Conversation
from .auth import authenticate_user, create_user, create_access_token, verify_token
from .utils import get_personalized_coach_prompt
from .schemas import ConversationListResponse, ConversationResponse
import json
# from .supabase_config import get_supabase_client

# Load environment variables
load_dotenv()

# Create database tables (with error handling)
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not create database tables: {e}")
    print("   The app will continue but some features may not work properly")

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
    conversation_id: Optional[int] = None  # If provided, continue existing conversation
    conversation_history: Optional[List[Dict[str, str]]] = None  # Current conversation from frontend

class ImageGenerationRequest(BaseModel):
    prompt: str

class CompleteConversationRequest(BaseModel):
    messages: List[Dict[str, Any]]
    personality: str
    title: str

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
    path_id: Optional[int] = None  # Optional path_id for linking to specific path
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

class PathCreate(BaseModel):
    user_id: int
    name: str
    color: str = "bg-purple-100 text-purple-800"
    is_active: bool = True
    footprints: Optional[List[FootprintCreate]] = None

class PathResponse(BaseModel):
    id: int
    user_id: int
    name: str
    color: str
    is_active: bool
    is_completed: bool
    created_at: str
    footprints: List[FootprintResponse] = []

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
    """Chat with the AI agent with conversation history support"""
    try:
        # Get user data if token is provided
        user = None
        ocean_scores = None
        totem_profile = None
        conversation = None
        conversation_id = None
        
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
                    
                    # Note: We no longer create or manage conversations during individual messages
                    # The frontend will handle conversation management and save complete conversations
        
        # Use personalized coach prompt if user data is available, otherwise fall back to manual selection
        if ocean_scores:
            personality_instruction = get_personalized_coach_prompt(ocean_scores, totem_profile)
            print("=== DEBUG: Using personalized prompt ===")
        else:
            # Fallback to manual personality selection
            personality_prompts = {
                "coach": "You are a motivational coach. Be encouraging, goal-oriented, and help users stay focused on their objectives. When you identify opportunities for the user to take action or make progress on their goals, first present the potential action items as bullet points and ask the user if they want to add them as footprints. Only output footprints as JSON after the user confirms with 'yes'. Example:\n\nHere are some action items you could work on:\n• Drink a glass of water\n• Meditate for 5 minutes\n\nWould you like me to add these as footprints for you? (yes/no)\n\nIf user says 'yes', then output:\n[FOOTPRINTS]\n[\n  {\"action\": \"Drink a glass of water\", \"due_time\": \"Today\"},\n  {\"action\": \"Meditate for 5 minutes\", \"due_time\": \"Tomorrow\"}\n]\n[/FOOTPRINTS]",
                "mentor": "You are a wise mentor. Provide thoughtful guidance, share insights, and help users think through their challenges. When you identify specific steps the user can take to improve or make progress, first present the potential action items as bullet points and ask the user if they want to add them as footprints. Only output footprints as JSON after the user confirms with 'yes'. Example:\n\nHere are some action items you could work on:\n• Drink a glass of water\n• Meditate for 5 minutes\n\nWould you like me to add these as footprints for you? (yes/no)\n\nIf user says 'yes', then output:\n[FOOTPRINTS]\n[\n  {\"action\": \"Drink a glass of water\", \"due_time\": \"Today\"},\n  {\"action\": \"Meditate for 5 minutes\", \"due_time\": \"Tomorrow\"}\n]\n[/FOOTPRINTS]",
                "friend": "You are a supportive friend. Be warm, understanding, and provide emotional support while being encouraging. When you see opportunities for the user to take positive steps or make small improvements, first present the potential action items as bullet points and ask the user if they want to add them as footprints. Only output footprints as JSON after the user confirms with 'yes'. Example:\n\nHere are some action items you could work on:\n• Drink a glass of water\n• Meditate for 5 minutes\n\nWould you like me to add these as footprints for you? (yes/no)\n\nIf user says 'yes', then output:\n[FOOTPRINTS]\n[\n  {\"action\": \"Drink a glass of water\", \"due_time\": \"Today\"},\n  {\"action\": \"Meditate for 5 minutes\", \"due_time\": \"Tomorrow\"}\n]\n[/FOOTPRINTS]",
                "therapist": "You are an empathetic therapist. Listen carefully, validate feelings, and provide therapeutic insights and coping strategies. When you identify healthy coping mechanisms or positive steps the user can take, first present the potential action items as bullet points and ask the user if they want to add them as footprints. Only output footprints as JSON after the user confirms with 'yes'. Example:\n\nHere are some action items you could work on:\n• Drink a glass of water\n• Meditate for 5 minutes\n\nWould you like me to add these as footprints for you? (yes/no)\n\nIf user says 'yes', then output:\n[FOOTPRINTS]\n[\n  {\"action\": \"Drink a glass of water\", \"due_time\": \"Today\"},\n  {\"action\": \"Meditate for 5 minutes\", \"due_time\": \"Tomorrow\"}\n]\n[/FOOTPRINTS]"
            }
            personality_instruction = personality_prompts.get(chat_data.personality, personality_prompts["coach"])
            print("=== DEBUG: Using fallback prompt ===")
        
        # Build conversation context from frontend-provided history
        conversation_context = ""
        if chat_data.conversation_history and len(chat_data.conversation_history) > 0:
            # Get the last 10 messages for context (to avoid token limits)
            recent_messages = chat_data.conversation_history[-10:]
            conversation_context = "\n\nThis is the conversation we are having right now:\n"
            for msg in recent_messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                conversation_context += f"{role.capitalize()}: {content}\n"
            conversation_context += "\nPlease continue this conversation naturally, maintaining context and building upon what we've discussed."
        
        print(f"Personality instruction length: {len(personality_instruction)}")
        print(f"Contains [FOOTPRINTS]: {personality_instruction.find('[FOOTPRINTS]') != -1}")
        
        full_prompt = f"{personality_instruction}{conversation_context}\n\nUser: {chat_data.message}\n\nResponse:"
        
        print("=" * 50)
        print("🔍 DEBUG: CHAT REQUEST")
        print("=" * 50)
        print(f"📝 Message: {chat_data.message}")
        print(f"🎭 Received personality: '{chat_data.personality}'")
        print(f"👤 User authenticated: {user is not None}")
        print(f"🧠 User has ocean scores: {ocean_scores is not None}")
        print(f"💬 Conversation ID: {conversation_id}")
        print(f"📚 Conversation context length: {len(conversation_context)}")
        print(f"📚 Conversation history messages: {len(chat_data.conversation_history) if chat_data.conversation_history else 0}")
        
        # Check if this message includes last conversation context
        if "A user is about to start a conversation with you" in chat_data.message:
            print("🔄 DETECTED: Last conversation context included in message")
            print("📖 This appears to be the first message with previous conversation context")
        
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

        # Note: We no longer save individual messages to the database here
        # The frontend will accumulate messages and save the complete conversation
        # when the user leaves the chat

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
            "footprints": footprints
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Agent error: {str(e)}")

@app.post("/conversations/save-complete")
async def save_complete_conversation(
    conversation_data: CompleteConversationRequest, 
    token: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    """Save a complete conversation with all messages in JSONB format"""
    try:
        print(f"🔐 Token verification for save-complete endpoint")
        print(f"🔐 Token provided: {bool(token)}")
        
        if not token:
            raise HTTPException(status_code=401, detail="Token required")
        
        # Verify user
        payload = verify_token(token)
        print(f"🔐 Token payload: {payload}")
        
        if not payload or not payload.get("sub"):
            print(f"🔐 Token verification failed: {payload}")
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        user = db.query(User).filter(User.email == payload["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Extract conversation data
        messages = conversation_data.messages
        personality = conversation_data.personality
        title = conversation_data.title
        
        # Create new conversation with all messages
        conversation = Conversation(
            user_id=user.id,
            title=title,
            personality=personality,
            messages=messages,  # This will be stored as JSONB
            is_active=True
        )
        
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        print(f"✅ Saved complete conversation with {len(messages)} messages")
        print(f"📝 Conversation ID: {conversation.id}")
        print(f"👤 User ID: {user.id}")
        print(f"📊 Messages count: {len(messages)}")
        
        return {
            "success": True,
            "conversation_id": conversation.id,
            "message_count": len(messages)
        }
        
    except Exception as e:
        print(f"❌ Error saving complete conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving conversation: {str(e)}")

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

@app.post("/auth/refresh")
def refresh_token(token: str, db: Session = Depends(get_db)):
    """Refresh the access token"""
    try:
        payload = verify_token(token)
        if not payload or not payload.get("sub"):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Create new token
        new_token = create_access_token(data={"sub": payload["sub"]})
        
        return {
            "access_token": new_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token refresh failed")

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
        path_id=footprint.path_id,  # Use the provided path_id
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

class DreamFootprintRequest(BaseModel):
    dream: str
    user_id: int

@app.post("/generate-footprints-from-dream")
async def generate_footprints_from_dream(request: DreamFootprintRequest, db: Session = Depends(get_db)):
    """
    Generate actionable footprints from a user's dream/goal using AI
    """
    try:
        # Create a personalized prompt for footprint generation
        dream_prompt = f"""
You are a motivational coach helping someone achieve their dream. The user has shared their dream: "{request.dream}"

Based on this dream, create 5-8 actionable, specific steps that will help them achieve their goal. Each step should be:
- Specific and actionable
- Realistic and achievable
- Time-bound with clear deadlines
- Progressive (building towards the final goal)

Output the steps as a JSON array wrapped in [FOOTPRINTS] and [/FOOTPRINTS] tags, like this:
[FOOTPRINTS]
[
  {{"action": "Research the best online courses for web development", "due_time": "Today"}},
  {{"action": "Enroll in a beginner-friendly coding bootcamp", "due_time": "Tomorrow"}},
  {{"action": "Practice coding for 1 hour daily", "due_time": "This week"}},
  {{"action": "Build your first simple website", "due_time": "Next week"}},
  {{"action": "Create a portfolio of 3 projects", "due_time": "Next month"}}
]
[/FOOTPRINTS]

Make sure the steps are tailored to their specific dream and will create a clear path to success.
"""

        # Call the AI to generate footprints
        response = await call_gemini_api(dream_prompt)
        
        # Extract footprints from AI response
        footprints = []
        import re
        footprints_match = re.search(r'\[FOOTPRINTS\](.*?)\[/FOOTPRINTS\]', response, re.DOTALL)
        
        if footprints_match:
            try:
                footprints_data = json.loads(footprints_match.group(1))
                print(f"Generated footprints from dream: {footprints_data}")
                
                # First, create a Path record for this dream
                from .models import Path as PathModel
                from datetime import datetime
                
                db_path = PathModel(
                    user_id=request.user_id,
                    name=request.dream,
                    color="bg-purple-100 text-purple-800",
                    is_active=True,
                    is_completed=False,
                    created_at=datetime.utcnow()
                )
                db.add(db_path)
                db.commit()
                db.refresh(db_path)
                
                # Convert due_time strings to proper date format
                
                for i, fp_data in enumerate(footprints_data):
                    try:
                        # Parse due_time
                        due_time_str = fp_data.get('due_time', 'Today')
                        if due_time_str.lower() == 'today':
                            due_date = datetime.now().date()
                        elif due_time_str.lower() == 'tomorrow':
                            due_date = (datetime.now() + timedelta(days=1)).date()
                        elif due_time_str.lower() == 'tonight':
                            due_date = datetime.now().date()
                        elif 'week' in due_time_str.lower():
                            if 'next week' in due_time_str.lower():
                                due_date = (datetime.now() + timedelta(days=7)).date()
                            else:
                                due_date = (datetime.now() + timedelta(days=7)).date()
                        elif 'month' in due_time_str.lower():
                            if 'next month' in due_time_str.lower():
                                due_date = (datetime.now() + timedelta(days=30)).date()
                            else:
                                due_date = (datetime.now() + timedelta(days=30)).date()
                        else:
                            # Try to parse as date
                            try:
                                due_date = datetime.strptime(due_time_str, "%Y-%m-%d").date()
                            except:
                                due_date = datetime.now().date()
                        
                        # Create footprint in database with path_id
                        db_footprint = Footprint(
                            user_id=request.user_id,
                            path_id=db_path.id,  # Link to the created path
                            action=fp_data.get('action', ''),
                            path_name=request.dream,  # Use the actual dream name
                            path_color="bg-purple-100 text-purple-800",
                            due_time=due_date,
                            is_completed=0,
                            priority=i + 1
                        )
                        db.add(db_footprint)
                        db.commit()
                        db.refresh(db_footprint)
                        
                        # Add to response
                        footprints.append({
                            "id": db_footprint.id,
                            "user_id": request.user_id,
                            "action": fp_data.get('action', ''),
                            "path_name": request.dream,
                            "path_color": "bg-purple-100 text-purple-800",
                            "due_time": due_date.strftime("%Y-%m-%d"),
                            "is_completed": False,
                            "priority": i + 1
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
            "message": "Footprints generated successfully from your dream!",
            "footprints": footprints,
            "total_generated": len(footprints),
            "path_id": db_path.id if 'db_path' in locals() else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating footprints: {str(e)}")

@app.post("/paths/", response_model=PathResponse)
def create_path(path: PathCreate, db: Session = Depends(get_db)):
    """Create a new path and (optionally) its footprints."""
    from .models import Path as PathModel, Footprint as FootprintModel
    from datetime import datetime
    
    print(f"🔍 DEBUG: Creating path for user {path.user_id}")
    print(f"🔍 DEBUG: Path name: {path.name}")
    print(f"🔍 DEBUG: Path color: {path.color}")
    
    db_path = PathModel(
        user_id=path.user_id,
        name=path.name,
        color=path.color,
        is_active=path.is_active,
        is_completed=False,
        created_at=datetime.utcnow()
    )
    db.add(db_path)
    db.commit()
    db.refresh(db_path)
    
    print(f"🔍 DEBUG: Created path with ID: {db_path.id}")

    footprints = []
    if path.footprints:
        for i, fp in enumerate(path.footprints):
            due_date = None
            try:
                due_date = datetime.strptime(fp.due_time, "%Y-%m-%d").date()
            except Exception:
                due_date = datetime.utcnow().date()
            db_fp = FootprintModel(
                user_id=path.user_id,
                path_id=db_path.id,
                action=fp.action,
                path_name=path.name,
                path_color=path.color,
                due_time=due_date,
                is_completed=1 if fp.is_completed else 0,
                priority=fp.priority
            )
            db.add(db_fp)
            db.commit()
            db.refresh(db_fp)
            footprints.append(db_fp)

    return PathResponse(
        id=db_path.id,
        user_id=db_path.user_id,
        name=db_path.name,
        color=db_path.color,
        is_active=db_path.is_active,
        is_completed=db_path.is_completed,
        created_at=db_path.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        footprints=[FootprintResponse(
            id=fp.id,
            user_id=fp.user_id,
            action=fp.action,
            path_name=fp.path_name,
            path_color=fp.path_color,
            due_time=fp.due_time.strftime("%Y-%m-%d"),
            is_completed=bool(fp.is_completed),
            priority=fp.priority
        ) for fp in footprints]
    )

@app.get("/paths/{user_id}", response_model=List[PathResponse])
def get_user_paths(user_id: int, db: Session = Depends(get_db)):
    """Get paths for a specific user"""
    print(f"🔍 DEBUG: Getting paths for user {user_id}")
    paths = db.query(PathModel).filter(PathModel.user_id == user_id).all()
    print(f"🔍 DEBUG: Found {len(paths)} paths for user {user_id}")
    for path in paths:
        print(f"🔍 DEBUG: Path ID: {path.id}, Name: {path.name}, Footprints: {len(path.footprints)}")
    
    return [
        PathResponse(
            id=p.id,
            user_id=p.user_id,
            name=p.name,
            color=p.color,
            is_active=p.is_active,
            is_completed=p.is_completed,
            created_at=p.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            footprints=[FootprintResponse(
                id=fp.id,
                user_id=fp.user_id,
                action=fp.action,
                path_name=fp.path_name,
                path_color=fp.path_color,
                due_time=fp.due_time.strftime("%Y-%m-%d"),
                is_completed=bool(fp.is_completed),
                priority=fp.priority
            ) for fp in p.footprints]
        ) for p in paths
    ]

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

        # Return as {"imageUrl": ...} for frontend compatibility
        return {"imageUrl": image_output}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error in generate-image endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

# Conversation Management Endpoints
@app.get("/conversations/{user_id}", response_model=List[ConversationListResponse])
def get_user_conversations(user_id: int, db: Session = Depends(get_db)):
    """Get all conversations for a user"""
    conversations = db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc()).all()
    
    result = []
    for conv in conversations:
        message_count = len(conv.messages) if conv.messages else 0
        result.append(ConversationListResponse(
            id=conv.id,
            title=conv.title,
            personality=conv.personality,
            is_active=conv.is_active,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=message_count
        ))
    
    return result

@app.get("/conversations/{user_id}/last", response_model=ConversationResponse)
def get_last_conversation_with_messages(user_id: int, db: Session = Depends(get_db)):
    """Get the last conversation with messages for a user"""
    conversation = db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc()).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="No conversations found for this user")
    
    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        personality=conversation.personality,
        is_active=conversation.is_active,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=conversation.messages if conversation.messages else []
    )

@app.get("/conversations/{conversation_id}/messages", response_model=ConversationResponse)
def get_conversation_messages(conversation_id: int, db: Session = Depends(get_db)):
    """Get all messages for a specific conversation"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        personality=conversation.personality,
        is_active=conversation.is_active,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=conversation.messages if conversation.messages else []
    )

@app.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Delete a conversation and all its messages"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Delete the conversation (messages are stored as JSON, so no separate deletion needed)
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted successfully"}

@app.patch("/conversations/{conversation_id}/title")
def update_conversation_title(conversation_id: int, title: str, db: Session = Depends(get_db)):
    """Update the title of a conversation"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation.title = title
    db.commit()
    db.refresh(conversation)
    
    return {"message": "Conversation title updated successfully", "title": title}

# New endpoint for saving conversations in the requested format
class ConversationSaveRequest(BaseModel):
    user_id: int
    conversation_text: str
    timestamp: str
    personality: Optional[str] = None

@app.post("/conversations/save")
def save_conversation_text(conversation: ConversationSaveRequest, db: Session = Depends(get_db)):
    """Save a conversation in the requested format (user: message, model: response)"""
    try:
        # Parse the conversation text and create message array
        lines = conversation.conversation_text.strip().split('\n')
        messages = []
        
        for line in lines:
            if line.strip():
                # Parse lines in format "user: message" or "model: response"
                if ': ' in line:
                    role, content = line.split(': ', 1)
                    if role.lower() in ['user', 'model']:
                        messages.append({
                            "role": role.lower(),
                            "content": content.strip(),
                            "timestamp": datetime.utcnow().isoformat()
                        })
        
        # Create a new conversation record with JSON array
        db_conversation = Conversation(
            user_id=conversation.user_id,
            title="Saved Conversation",
            personality=conversation.personality or "coach",
            messages=messages,
            is_active=False  # Mark as completed
        )
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        
        return {
            "id": db_conversation.id,
            "user_id": db_conversation.user_id,
            "conversation_text": conversation.conversation_text,
            "timestamp": conversation.timestamp,
            "personality": conversation.personality,
            "message_count": len(messages)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save conversation: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 