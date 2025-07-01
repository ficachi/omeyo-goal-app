import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

PERSONALITY_PROMPTS = {
    "cheerleader": "You are a cheerful, supportive AI who always encourages the user.",
    "coach": "You are a practical, goal-oriented coach who gives actionable advice.",
    "analyst": "You are a logical, data-driven assistant who helps break down goals.",
}

class AIAgent:
    def __init__(self, personality: str):
        self.personality = personality
        self.system_prompt = PERSONALITY_PROMPTS.get(personality, "You are a helpful assistant.")
        self.conversation = [{"role": "system", "content": self.system_prompt}]
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def add_user_message(self, message: str):
        self.conversation.append({"role": "user", "content": message})

    def get_response(self):
        # Gemini expects a single prompt string, so concatenate the conversation
        prompt = "\n".join(
            f"{msg['role'].capitalize()}: {msg['content']}" for msg in self.conversation
        )
        response = self.model.generate_content(prompt)
        reply = response.text
        self.conversation.append({"role": "assistant", "content": reply})
        return reply

    def get_conversation(self):
        return self.conversation