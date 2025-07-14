#!/usr/bin/env python3
"""
Test script to check Vertex AI access and available models
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_vertex_access():
    """Test Vertex AI access and list available models"""
    try:
        import vertexai
        
        # Initialize Vertex AI
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "gen-lang-client-0204395031")
        print(f"Testing Vertex AI access for project: {project_id}")
        
        vertexai.init(project=project_id, location="us-central1")
        print("✅ Vertex AI initialized successfully")
        
        # Try to list models
        try:
            from vertexai.preview.vision_models import ImageGenerationModel
            
            # Test different model names
            models_to_test = [
                "imagen-3.0-generate-002",
                "imagen-4.0-generate-preview-06-06",
                "imagen-2.0",
                "imagen-1.0"
            ]
            
            print("\n🔍 Testing model access:")
            for model_name in models_to_test:
                try:
                    print(f"Testing: {model_name}")
                    model = ImageGenerationModel.from_pretrained(model_name)
                    print(f"✅ {model_name} is accessible!")
                    return model_name
                except Exception as e:
                    print(f"❌ {model_name}: {str(e)[:100]}...")
            
            print("\n❌ No accessible image generation models found")
            
        except Exception as e:
            print(f"❌ Error accessing ImageGenerationModel: {e}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_vertex_access() 