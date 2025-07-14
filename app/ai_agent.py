import os
import base64
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

async def generate_image_with_imagen(prompt: str) -> str:
    """
    Generates an image using Imagen REST API based on the provided prompt.
    Returns the URL of the generated image or an error message.
    """
    try:
        # Check if Google Cloud credentials are available from environment variable
        encoded_credentials = os.getenv("GOOGLE_CLOUD_CREDENTIALS")
        if not encoded_credentials:
            print("Google Cloud credentials not found. Using placeholder image for development.")
            # Return a simple base64 encoded placeholder image
            # Simple 1x1 pixel PNG image with blue background
            placeholder_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            return f"data:image/png;base64,{placeholder_base64}"
        
        import requests
        import json
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
        
        # Get project ID
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "gen-lang-client-0204395031")
        
        # Decode the base64 credentials and load service account credentials
        try:
            # Decode the base64 string
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            
            # Parse the JSON
            credentials_dict = json.loads(decoded_credentials)
            
            # Create credentials from dictionary
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            credentials.refresh(Request())
            access_token = credentials.token
        except Exception as e:
            print(f"Error getting access token: {e}")
            # Return a simple base64 encoded placeholder image
            # Simple 1x1 pixel PNG image with blue background
            placeholder_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            return f"data:image/png;base64,{placeholder_base64}"
        
        # Prepare the request
        url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/google/models/imagen-4.0-generate-preview-06-06:predict"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        data = {
            "instances": [
                {
                    "prompt": f"{prompt}, photorealistic, no text, forward-looking view"
                }
            ],
            "parameters": {
                "sampleCount": 1
            }
        }
        
        # Make the request
        print(f"🖼️ Generating image with prompt: {prompt}")
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if "predictions" in result and len(result["predictions"]) > 0:
                # Get the base64 encoded image
                image_data = result["predictions"][0]["bytesBase64Encoded"]
                return f"data:image/png;base64,{image_data}"
            else:
                print("No predictions in response")
                return "Error: No images were generated."
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return f"Error: {response.status_code} - {response.text}"
            
    except ImportError as e:
        print(f"Error: Required libraries not installed: {e}")
        return "Error: Image generation library not installed."
    except Exception as e:
        print(f"Error generating image with Imagen: {e}")
        # Fallback to placeholder image
        # Simple 1x1 pixel PNG image with blue background
        placeholder_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        return f"data:image/png;base64,{placeholder_base64}"