from pydantic import BaseModel
from typing import Literal

class ChatRequest(BaseModel):
    message: str
    personality: Literal['Default', 'Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism']

class ChatResponse(BaseModel):
    response: str
