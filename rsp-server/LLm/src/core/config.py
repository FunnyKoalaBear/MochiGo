import json
import os

CONFIG_FILE = "rsp-server/LLm/data/mochigo_config.json"

def load_config():
    """Loads the user's persistent save data, or creates a default one."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
            
    # Default fresh save file
    # Default fresh save file
    default_config = {
        "is_first_boot": True,
        "user_level": "beginner",
        "speech_practice_count": 0,
        "struggling_points": [], # <--- NEW: Add this to the default save!
        "taught_concepts": {
            "definition": [],
            "language_concept": []
        }
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    save_config(default_config)
    
    return default_config

def save_config(config_data):
    """Saves the user's data to the hard drive."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)