from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="Omeyo AI Coach API",
    description="API for interacting with the Omeyo AI Coach, featuring personality-based responses.",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to Omeyo AI Coach API!"}

# Imports for the chat endpoint
from .schemas import ChatRequest, ChatResponse
from .utils import get_personality_prompt
from .ai_agent import call_gemini_api

@app.post("/chat", response_model=ChatResponse)
async def chat_with_coach(request: ChatRequest):
    # 1. Get the personality-specific instructions
    personality_instruction = get_personality_prompt(request.personality)

    # 2. Construct the full prompt for the Gemini API
    full_prompt = f"{personality_instruction} Now, respond to the following user request: {request.message}"

    # 3. Call the Gemini API with the full prompt
    ai_response_text = await call_gemini_api(full_prompt)

    return ChatResponse(response=ai_response_text)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)