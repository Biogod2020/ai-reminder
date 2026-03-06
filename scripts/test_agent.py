import requests
import json
import sys

def run_chat():
    base_url = "http://localhost:8000"
    history = []
    
    print("=== NSA Backend CLI Tester ===")
    print("Type 'exit' or 'quit' to stop.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        payload = {
            "message": user_input,
            "history": history
        }
        
        try:
            response = requests.post(f"{base_url}/chat", json=payload)
            response.raise_for_status()
            result = response.json()
            
            print(f"\n[Intent: {result['intent']}]")
            print(f"Agent: {result['response']}")
            
            if result.get("proposed_actions"):
                print("Proposed Actions:")
                for i, action in enumerate(result["proposed_actions"]):
                    print(f"  {i+1}. {action['title']} (Load: {action.get('estimated_cognitive_load')})")
            
            print("-" * 30)
            
            # Update history
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": result["response"]})
            
        except Exception as e:
            print(f"Error connecting to backend: {e}")

if __name__ == '__main__':
    run_chat()
