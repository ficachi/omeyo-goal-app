import requests
import json

def test_save_complete_conversation():
    """Test the new complete conversation saving endpoint"""
    
    # Test data
    conversation_data = {
        "messages": [
            {
                "role": "user",
                "content": "hello",
                "timestamp": "2025-07-15T17:02:02.935689"
            },
            {
                "role": "assistant", 
                "content": "Hello there! It's lovely to connect with you. How are you feeling today?",
                "timestamp": "2025-07-15T17:02:02.935696"
            },
            {
                "role": "user",
                "content": "how are you?",
                "timestamp": "2025-07-15T17:02:02.935697"
            },
            {
                "role": "assistant",
                "content": "I'm here and ready to help! How are you feeling today?",
                "timestamp": "2025-07-15T17:02:02.935700"
            }
        ],
        "personality": "The Caretaker",
        "title": "hello"
    }
    
    # You'll need to replace this with a valid token
    token = "your_test_token_here"
    
    url = f"http://localhost:8000/conversations/save-complete?token={token}"
    
    try:
        response = requests.post(url, json=conversation_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Test passed! Conversation saved successfully")
        else:
            print("❌ Test failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_save_complete_conversation() 