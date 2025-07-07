# Import the complete API from api.py
from .api import app
import os

if __name__ == "__main__":
    import uvicorn
    # Use Railway's PORT environment variable, fallback to 8000 for local development
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)