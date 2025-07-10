#!/usr/bin/env python3
"""
Script to list available Google Generative AI models
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def list_generative_models():
    """List available Google Generative AI models"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not set in .env file")
            return
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        print("🔍 Listing available Google Generative AI models...")
        print("=" * 60)
        
        # List all models
        models = list(genai.list_models())
        
        if not models:
            print("❌ No models found")
            return
        
        print(f"✅ Found {len(models)} model(s):")
        
        # Filter for image generation models
        image_models = []
        text_models = []
        
        for model in models:
            model_name = model.name
            if 'imagen' in model_name.lower() or 'image' in model_name.lower():
                image_models.append(model_name)
            else:
                text_models.append(model_name)
        
        print("\n🎨 Image Generation Models:")
        if image_models:
            for model in image_models:
                print(f"   - {model}")
        else:
            print("   No image generation models found")
        
        print("\n📝 Text Generation Models:")
        for model in text_models[:10]:  # Show first 10 text models
            print(f"   - {model}")
        
        if len(text_models) > 10:
            print(f"   ... and {len(text_models) - 10} more text models")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure google-generativeai is installed")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_generative_models() 