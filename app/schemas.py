from pydantic import BaseModel
from typing import Literal, List, Optional, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    personality: Literal['Default', 'Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism']
    conversation_id: Optional[int] = None  # If provided, continue existing conversation

class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    conversation_title: str

class ConversationBase(BaseModel):
    title: str
    personality: str = "coach"

class ConversationCreate(ConversationBase):
    user_id: int

class ConversationResponse(ConversationBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    messages: List[Dict[str, Any]] = []  # JSON array of messages

    class Config:
        from_attributes = True

class ConversationListResponse(BaseModel):
    id: int
    title: str
    personality: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    message_count: int

    class Config:
        from_attributes = True

class ConversationSaveRequest(BaseModel):
    user_id: int
    conversation_text: str
    timestamp: str
    personality: Optional[str] = None
