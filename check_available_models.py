#!/usr/bin/env python3
"""
Check what Vertex AI models are available in the current project
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_available_models():
    """Check what models are available"""
    try:
        import vertexai
        
        # Initialize Vertex AI
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "gen-lang-client-0204395031")
        print(f"Checking available models for project: {project_id}")
        
        vertexai.init(project=project_id, location="us-central1")
        print("✅ Vertex AI initialized successfully")
        
        # Try to list models (this might not work due to permissions)
        try:
            models = vertexai.Model.list()
            print(f"✅ Found {len(models)} models")
            for model in models:
                print(f"  - {model.display_name} ({model.name})")
        except Exception as e:
            print(f"❌ Could not list models: {e}")
        
        # Test specific model access
        models_to_test = [
            "imagen-3.0-generate-002",
            "imagen-4.0-generate-preview-06-06",
            "imagen-2.0",
            "gemini-2.0-flash-exp-image-generation",
            "gemini-2.0-flash-preview-image-generation"
        ]
        
        print("\n🔍 Testing specific model access:")
        accessible_models = []
        
        for model_name in models_to_test:
            try:
                from vertexai.preview.vision_models import ImageGenerationModel
                model = ImageGenerationModel.from_pretrained(model_name)
                print(f"✅ {model_name} - ACCESSIBLE")
                accessible_models.append(model_name)
            except Exception as e:
                print(f"❌ {model_name} - {str(e)[:100]}...")
        
        if accessible_models:
            print(f"\n✅ Accessible models: {accessible_models}")
            return accessible_models[0]  # Return the first accessible model
        else:
            print("\n❌ No accessible image generation models found")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    check_available_models() 