import json
import os
from langchain_core.messages import messages_to_dict

CONFIG_FILE = "rsp-server/LLm/data/mochigo_config.json"
HISTORY_FILE = "rsp-server/LLm/data/chat_history.json"

def load_config():
    """Loads the user's persistent save data, or creates a default one."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
            
    # Default fresh save file
    default_config = {
        "is_first_boot": True,
        "user_level": "beginner",
        "speech_practice_count": 0,
        "struggling_points": [], # <--- NEW: Add this to the default save!
        "taught_concepts": {
            "definition": [],
            "language_concept": []
        },
        "user_persona": {
            "likes": [],
            "dislikes": [],
            "mood_trends": "Unknown"
        },
        "optimal_learning_style": "Standard interactive learning.",
        "current_weekly_strategy": "Be friendly, patient, and encouraging. Focus on basic conversational English.",
        "strategy_history": []
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    save_config(default_config)
    
    return default_config

def save_config(config_data):
    """Saves the user's data to the hard drive."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)

def save_chat_history(messages):
    """Saves the entire LangGraph message array to a readable JSON file."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    
    # Convert LangChain objects to standard Python dictionaries
    msg_dicts = messages_to_dict(messages)
    
    # ensure_ascii=False is CRITICAL so Japanese characters don't turn into \u3042 gibberish!
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(msg_dicts, f, indent=4, ensure_ascii=False)