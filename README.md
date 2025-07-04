# Omeyo Backend

This is the backend for the Omeyo project, located in the `backend/` folder at the root of the repository.

## 🚀 Quick Start

### 1. Set up the virtual environment
```sh
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy and edit the environment file:
```sh
copy env.example .env  # Windows
# cp env.example .env  # Linux/Mac
```
Edit `.env` with your credentials.

### 3. Start the Backend Server
```sh
python -m app.main
```

Or use the root-level `start-dev.bat` script to start both backend and frontend together.

## 📡 API Endpoints

- **POST** `/chat` — Chat with AI Agent
- **POST** `/users/` — Create user
- **GET** `/users/` — Get all users
- **POST** `/goals/` — Create goal
- **GET** `/goals/{user_id}` — Get user goals
- **GET** `/health` — Health check
- **GET** `/supabase-test` — Test Supabase connection

## 🏗️ Architecture

- `app/main.py` — FastAPI application
- `app/api.py` — API routes
- `app/ai_agent.py` — AI agent logic
- `app/models.py` — Database models
- `app/database.py` — Database configuration

## Troubleshooting
- **Port 8000 already in use**: Change port in `app/main.py`
- **Database connection failed**: Check `DATABASE_URL` in `.env`
- **API calls failing**: Ensure backend is running on port 8000

For more details, see the main `README.md` at the project root. 