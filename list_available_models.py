#!/usr/bin/env python3
"""
Script to list available Vertex AI models
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def list_available_models():
    """List available Vertex AI models"""
    try:
        from google.cloud import aiplatform
        
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "596007567974")
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location="us-central1")
        
        print(f"🔍 Listing available models for project: {project_id}")
        print("=" * 60)
        
        # List all models
        models = aiplatform.Model.list()
        
        if not models:
            print("❌ No models found. This could mean:")
            print("   - Vertex AI API is not enabled")
            print("   - No models are deployed in this project")
            print("   - You don't have permission to list models")
        else:
            print(f"✅ Found {len(models)} model(s):")
            for model in models:
                print(f"   - {model.display_name} ({model.name})")
        
        # Try to list publishers
        print("\n🔍 Checking available publishers...")
        try:
            # This might not work depending on permissions
            publishers = aiplatform.Model.list_publishers()
            if publishers:
                print("Available publishers:")
                for publisher in publishers:
                    print(f"   - {publisher}")
            else:
                print("No publishers found or access denied")
        except Exception as e:
            print(f"Could not list publishers: {e}")
        
        # Check specific Imagen models
        print("\n🎨 Checking Imagen models specifically...")
        imagen_models = [
            "imagen-2.0",
            "imagen-1.0",
            "imagen-2.0-001",
            "imagen-1.0-001"
        ]
        
        for model_version in imagen_models:
            try:
                model_name = f"projects/{project_id}/locations/us-central1/publishers/google/models/{model_version}"
                print(f"Testing: {model_version}")
                endpoint = aiplatform.Endpoint(model_name)
                print(f"✅ {model_version} is accessible!")
                return model_version
            except Exception as e:
                print(f"❌ {model_version}: {str(e)[:100]}...")
        
        print("\n❌ No Imagen models are accessible")
        print("\n💡 To fix this:")
        print("1. Go to Google Cloud Console > Vertex AI > Generative AI Studio")
        print("2. Click on 'Image Generation' (Imagen)")
        print("3. Accept the terms of service")
        print("4. Wait a few minutes for the model to be enabled")
        
    except ImportError:
        print("❌ google-cloud-aiplatform not installed")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_available_models() 