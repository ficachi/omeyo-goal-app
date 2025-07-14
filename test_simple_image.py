#!/usr/bin/env python3
"""
Simple test for image generation with minimal parameters
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_simple_image():
    """Test simple image generation"""
    try:
        from vertexai.preview.vision_models import ImageGenerationModel
        import vertexai
        
        # Initialize Vertex AI
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "596007567974")
        print(f"Testing simple image generation for project: {project_id}")
        
        vertexai.init(project=project_id, location="us-central1")
        print("✅ Vertex AI initialized successfully")
        
        # Create model
        model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")
        print("✅ Model created successfully")
        
        # Try to generate with minimal parameters
        print("🖼️ Generating image...")
        images = model.generate_images(
            prompt="A simple red circle",
            number_of_images=1
        )
        
        print("✅ Image generation successful!")
        print(f"Generated {len(images)} image(s)")
        
        # Try to access the first image
        if images and len(images) > 0:
            print("✅ First image accessible")
            # Try to get the PIL image
            pil_image = images[0]._pil_image
            print(f"✅ PIL image created: {pil_image.size}")
            return True
        else:
            print("❌ No images generated")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_simple_image() 