from google import genai
from google.genai import types
client = genai.Client(api_key="AIzaSyAuMAXgYUDbVbUO3JolByFLfG-IjR1oNi4")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="You are a cat. Your name is Neko."),
    contents="Hello there"
)

print(response.text)