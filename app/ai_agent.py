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
    model = genai.GenerativeModel("gemini-1.5-flash-latest") # Using gemini-1.5-flash as per original, updated to latest
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
    Generates an image using Imagen (via Vertex AI) based on the provided prompt.
    Specifies no text on the image and a forward-looking view.
    Returns the URL of the generated image or an error message.
    """
    try:
        # This import is here as it's specific to this function.
        # Ensure you have GOOGLE_APPLICATION_CREDENTIALS set in your environment
        # or are authenticated in another way for Google Cloud.
        from google.cloud import aiplatform
        from google.protobuf import json_format
        from google.protobuf.struct_pb2 import Value
        PROJECT_ID = "596007567974" # Make sure this is your actual project ID

        # Initialize Vertex AI
        aiplatform.init(project=PROJECT_ID, location="us-central1")

        # Configure the Imagen model
        # Model name might vary, check documentation for the latest one for text-to-image
        model_name = "imagegeneration@005" # Example model, verify correct one
        endpoint = aiplatform.Endpoint(model_name)

        # Parameters for the image generation
        # Refer to Vertex AI Imagen documentation for all available parameters
        # https://cloud.google.com/vertex-ai/docs/generative-ai/image/generate-images
        parameters = {
            "prompt": f"{prompt}, no text, photorealistic, forward-looking view",
            "sampleCount": 1, # Number of images to generate
            # Add other parameters as needed, e.g., aspectRatio, negativePrompt
            # For "no text", it's usually part of the prompt or a specific parameter if available.
            # If there's a specific parameter to exclude text, it should be used.
            # Otherwise, including "no text" in the prompt is a common approach.
        }

        instances = [{"prompt": parameters["prompt"], "sample_count": parameters["sampleCount"]}] # Adjust based on actual API

        # The predict method and its parameters might vary based on the SDK version and model
        # This is a general representation.
        response = endpoint.predict(instances=instances)

        # Process the response to get the image URL or data
        # The response structure depends on the Imagen API version.
        # This is a placeholder for actual response parsing.
        # Assuming the response contains a list of predictions, and each prediction has image data (e.g., bytes or URL)
        if response.predictions:
            # This part needs to be adapted based on the actual structure of 'response.predictions'
            # For example, if it returns GCS URIs:
            # image_uri = response.predictions[0]['bytesGcsUri']
            # Or if it returns direct image bytes (less common for large images via API, might be base64 encoded)
            # image_bytes_b64 = response.predictions[0]['imageBytes']
            # For now, let's assume it's a direct URL or we need to construct one.
            # This is highly dependent on the specific Imagen model version and Vertex AI SDK.

            # Placeholder: Replace with actual logic to extract image URL or data
            # This is a common way to get results, but you'll need to check the exact response fields.
            generated_images = response.predictions[0] # Accessing the first prediction object/dict

            # Let's assume `generated_images` is a dict and might contain a URL or GCS path
            if 'url' in generated_images:
                return generated_images['url']
            elif 'gcsUri' in generated_images:
                # If it's a GCS URI, you might need to make it publicly accessible or handle it differently
                return generated_images['gcsUri']
            elif 'bytesBase64Encoded' in generated_images:
                # Handle base64 encoded image data if needed
                return f"data:image/png;base64,{generated_images['bytesBase64Encoded']}"
            else:
                print(f"Unexpected response structure: {generated_images}")
                return "Error: Could not extract image from AI response."
        else:
            print(f"Error: Imagen response does not contain predictions. Full response: {response}")
            return "Error: AI service did not return an image."

    except ImportError:
        print("Error: google-cloud-aiplatform or its dependencies are not installed.")
        return "Error: Image generation library not installed."
    except Exception as e:
        print(f"Error generating image with Imagen: {e}")
        # Consider logging the full exception for debugging
        return f"Error generating image: {str(e)}"