import time
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from core.config import save_config

# Use the fast model to instantly grade the user's level
eval_llm = ChatOllama(model="llama3.2", temperature=0.0)

def run_onboarding(current_config):
    """Interviews the user on first boot to determine their English level."""
    print("WELCOME TO MOCHIGO!")
    print("AI: [[SERVO:90]] [[FACE:happy]] Hello! I am MochiGo! Since this is our first time meeting, I want to know how good your English is so we can have great conversations.")
    print("AI: Could you tell me a little bit about yourself, why you want to learn English, and what you think your current level is?")
    
    user_response = input("\nYou: ")
    
    print("\n[MochiGo is analyzing your English level...]")
    
    prompt = f"""You are an expert English teacher. Read the following introduction from a new Japanese student.
    
    Student's Introduction: "{user_response}"
    
    Based on their vocabulary, grammar complexity, and what they explicitly stated, categorize them into exactly ONE of these three levels:
    - beginner
    - intermediate
    - expert
    
    Output ONLY the exact word of the level. No punctuation, no explanation.
    """
    
    try:
        level = eval_llm.invoke([HumanMessage(content=prompt)]).content.strip().lower()
        if level not in ["beginner", "intermediate", "expert"]:
            level = "beginner" # Fallback
    except Exception:
        level = "beginner"
        
    # Update and save the config
    current_config["user_level"] = level
    current_config["is_first_boot"] = False
    save_config(current_config)
    
    print(f"\n[SYSTEM] Your difficulty has been permanently set to: {level.upper()}")
    print("AI: [[SERVO:100]] [[FACE:surprised]] Perfect! I have adjusted my brain. Let's start learning!")
    print("="*50 + "\n")
    
    time.sleep(2)
    return current_config