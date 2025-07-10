import asyncio
from app.ai_agent import generate_image_with_imagen

async def main():
    prompt = "A beautiful sunset over the mountains, photorealistic, no text"
    print(f"Testing image generation with prompt: {prompt}")
    result = await generate_image_with_imagen(prompt)
    print("Result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main()) 