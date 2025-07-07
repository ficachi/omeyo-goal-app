import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# The PERSONALITY_PROMPTS dictionary is removed as this logic is now handled by get_personality_prompt in utils.py
# The AIAgent class is removed as it's stateful and not suitable for the new API design.
# A new stateless function call_gemini_api is added.

# Initialize the generative model globally or ensure it's initialized before use.
# It's good practice to initialize this once if the model doesn't change.
try:
    model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17") # Using gemini-1.5-flash as per original, updated to latest
except Exception as e:
    print(f"Error initializing GenerativeModel: {e}")
    # Potentially raise the error or handle it as per application requirements
    # For now, we'll let it proceed, and it will fail at the point of use if 'model' is not set.
    model = None

async def call_gemini_api(full_prompt: str) -> str:
    """
    Calls the Gemini API with the given prompt and returns the response text.
    This is an asynchronous function.
    """
    if model is None:
        # This can happen if the genai.configure(api_key=...) failed or
        # genai.GenerativeModel(...) failed during startup.
        # Consider how to handle this robustly - e.g., re-initialize or raise an error.
        # For now, returning an error message.
        # In a real app, you might want to raise an HTTPException for FastAPI.
        print("Error: GenerativeModel is not initialized.")
        return "Error: AI service is not configured."

    try:
        # Assuming generate_content can be awaited if the SDK supports async,
        # or it needs to be run in a thread pool if it's blocking.
        # The google-generativeai library's generate_content is synchronous.
        # To make this function truly async and non-blocking for FastAPI,
        # the synchronous call should be wrapped with something like asyncio.to_thread.
        # For simplicity in this step, we'll call it directly.
        # If performance issues arise, this is an area for optimization.

        # response = await asyncio.to_thread(model.generate_content, full_prompt) # Example for true async
        response = model.generate_content(full_prompt) # Synchronous call

        # Ensure there's content and text before trying to access.
        if response and response.text:
            return response.text
        elif response and not response.text and response.candidates:
            # Sometimes the text might be empty but candidates might have content or safety issues
            # Log or handle as per requirements if parts or candidates exist
            print(f"Warning: Gemini response text is empty. Candidates: {response.candidates}")
            return "AI model returned an empty response."
        else:
            print("Warning: Gemini response or response.text is empty.")
            return "AI model returned an empty or unexpected response."
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        # In a FastAPI app, you might raise an HTTPException here.
        return f"Error communicating with AI service: {str(e)}"