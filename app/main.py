from app.ai_agent import AIAgent

def main():
    print("Welcome to Omeyo AI Agent Demo!")
    personality = input("Choose agent personality (cheerleader/coach/analyst): ")
    agent = AIAgent(personality)
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        agent.add_user_message(user_input)
        response = agent.get_response()
        print(f"Omeyo ({personality}): {response}\n")

if __name__ == "__main__":
    main() 