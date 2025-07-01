# Omeyo

Omeyo is a goal accomplishment app that uses AI agents with different personalities to help users achieve their goals. The AI agent's personality is matched to the user's own, or to a complementary style, to maximize motivation, engagement, and completion rates. The agent provides reminders, encouragement, and tailored strategies for each user.

## Features
- Personality-based AI agent (powered by GEMINI)
- Goal tracking and management
- Personalized reminders and strategies
- Conversation context protocol for continuity
- PostgreSQL database integration

## Setup
1. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your GEMINI and database credentials.
4. Initialize the database tables:
   ```sh
   python -m app.models
   ```
5. Run the main app:
   ```sh
   python -m app.main
   ``` 