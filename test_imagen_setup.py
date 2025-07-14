#!/usr/bin/env python3
"""
Test script to verify Google Cloud and Imagen setup
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_google_cloud_setup():
    """Test if Google Cloud is properly configured"""
    print("🔍 Testing Google Cloud Setup...")
    
    # Check environment variables
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    print(f"Project ID: {project_id or 'Not set'}")
    print(f"Credentials path: {credentials_path or 'Not set'}")
    
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT_ID not set in .env file")
        return False
    
    if not credentials_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set in .env file")
        return False
    
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found at: {credentials_path}")
        return False
    
    print("✅ Environment variables look good")
    
    # Test Google Cloud imports
    try:
        from google.cloud import aiplatform
        print("✅ google-cloud-aiplatform imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import google-cloud-aiplatform: {e}")
        return False
    
    # Test authentication
    try:
        aiplatform.init(project=project_id, location="us-central1")
        print("✅ Google Cloud authentication successful")
    except Exception as e:
        print(f"❌ Google Cloud authentication failed: {e}")
        return False
    
    return True

def test_imagen_access():
    """Test if Imagen is accessible using Vertex AI Endpoint"""
    print("\n🎨 Testing Imagen Access...")
    
    try:
        from google.cloud import aiplatform
        
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "596007567974")
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location="us-central1")
        
        # Test the model access
        model_name = f"projects/{project_id}/locations/us-central1/publishers/google/models/imagen-2.0"
        print(f"Testing model: {model_name}")
        
        endpoint = aiplatform.Endpoint(model_name)
        print("✅ Imagen model is accessible!")
        
        # Test a simple image generation
        print("Testing image generation...")
        response = endpoint.predict(
            instances=[{
                "prompt": "A beautiful sunset",
                "sample_count": 1
            }]
        )
        
        if response.predictions and len(response.predictions) > 0:
            print("✅ Image generation successful!")
            return True
        else:
            print("❌ No images generated")
            return False
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure google-cloud-aiplatform is installed")
        return False
    except Exception as e:
        print(f"❌ Imagen access failed: {e}")
        print("💡 Make sure you have enabled the Vertex AI API and Imagen in your Google Cloud project")
        return False

if __name__ == "__main__":
    print("🚀 Omeyo Image Generation Setup Test")
    print("=" * 50)
    
    # Test basic setup
    if not test_google_cloud_setup():
        print("\n❌ Basic setup failed. Please check your configuration.")
        sys.exit(1)
    
    # Test Imagen access
    if not test_imagen_access():
        print("\n❌ Imagen access failed. Please enable the required APIs.")
        sys.exit(1)
    
    print("\n✅ All tests passed! Your setup is ready for image generation.")
    print("\n📝 Next steps:")
    print("1. Restart your backend server")
    print("2. Test the image generation in your frontend")
    print("3. Enter a dream in the FutureDreamStep component") 