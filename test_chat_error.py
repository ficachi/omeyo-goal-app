import os
import sys

from app.database import SessionLocal
from app.models import User, Conversation
from app.auth import verify_token

def test_database_operations():
    """Test database operations to identify the issue"""
    db = SessionLocal()
    try:
        # Test 1: Check if we can query users
        print("Testing user query...")
        users = db.query(User).all()
        print(f"Found {len(users)} users")
        
        # Test 2: Check if we can query conversations
        print("Testing conversation query...")
        conversations = db.query(Conversation).all()
        print(f"Found {len(conversations)} conversations")
        
        # Test 3: Check conversation schema
        if conversations:
            conv = conversations[0]
            print(f"Conversation ID: {conv.id}")
            print(f"User ID: {conv.user_id}")
            print(f"Title: {conv.title}")
            print(f"Personality: {conv.personality}")
            print(f"Messages type: {type(conv.messages)}")
            print(f"Messages value: {conv.messages}")
            print(f"Is active: {conv.is_active}")
            print(f"Created at: {conv.created_at}")
            print(f"Updated at: {conv.updated_at}")
        
        # Test 4: Try to create a new conversation
        print("Testing conversation creation...")
        if users:
            user = users[0]
            new_conv = Conversation(
                user_id=user.id,
                title="Test Conversation",
                personality="coach",
                messages=[]
            )
            db.add(new_conv)
            db.commit()
            db.refresh(new_conv)
            print(f"Created conversation with ID: {new_conv.id}")
            
            # Test 5: Try to update messages
            print("Testing message update...")
            new_conv.messages = [
                {"role": "user", "content": "test", "timestamp": "2024-01-01T00:00:00"}
            ]
            db.commit()
            print("Successfully updated messages")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_database_operations() 