import sys
import os
# Force Python to see the 'src' folder as the root, regardless of how the script is run
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import os
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from core.config import load_config, save_config, HISTORY_FILE

# Use the big brain for deep psychological analysis
analyst_llm = ChatOllama(model="deepseek-v3.1:671b-cloud", temperature=0.2, format="json")
strategist_llm = ChatOllama(model="deepseek-v3.1:671b-cloud", temperature=0.7)

def load_chat_transcript():
    """Loads the raw JSON history and converts it into a readable text transcript."""
    if not os.path.exists(HISTORY_FILE):
        return ""
        
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        try:
            history = json.load(f)
        except:
            return ""
            
    transcript = ""
    # Only grab the last 200 messages to prevent context overflow
    for msg in history[-200:]:
        sender = msg.get("type", "unknown")
        content = msg.get("data", {}).get("content", "")
        # Skip system overrides to keep the focus on actual human interaction
        if sender == "system" or "[INTERNAL" in content or "[TEACHING" in content:
            continue
        transcript += f"{sender.upper()}: {content}\n"
        
    return transcript

def run_sleep_cycle():
    print("\n" + "="*50)
    print("🌙 INITIATING MOCHIGO SLEEP CYCLE (DATA CONSOLIDATION)")
    print("="*50)
    
    config = load_config()
    transcript = load_chat_transcript()
    
    if len(transcript.strip()) < 50:
        print("[!] Not enough conversation history to analyze. Going back to sleep.")
        return
        
    print("\n[1/3] Running Analyst Protocol: Extracting user psychology...")
    
    analyst_prompt = f"""Read the following transcript of an English tutoring session.
{transcript}

Analyze the HUMAN's personality, mood, and learning preferences.
Output ONLY a JSON object with these exact keys:
"likes": [List of specific topics or things the human enjoys talking about]
"dislikes": [List of things the human finds boring, annoying, or frustrating]
"mood_trends": (String) A brief summary of their general mood during this session.
"optimal_learning_style": (String) How do they respond to corrections? Do they like chatting, or formal lessons? How should a tutor talk to them to keep them engaged?
"""
    
    try:
        analysis_response = analyst_llm.invoke([HumanMessage(content=analyst_prompt)]).content.strip()
        
        # --- NEW: The JSON Cleaner ---
        # Strip out markdown backticks if the LLM gets stubborn
        clean_response = analysis_response
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.startswith("```"):
            clean_response = clean_response[3:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]
            
        clean_response = clean_response.strip()
        print(clean_response)  # Debug print to see the cleaned JSON before parsing
        
        # Now parse the cleaned string
        analysis_data = json.loads(clean_response)

        if "user_persona" not in config:
            config["user_persona"] = {"likes": [], "dislikes": [], "mood_trends": "Unknown"}
        
        # Update config with new psychological profile
        config["user_persona"]["likes"] = analysis_data.get("likes", config["user_persona"].get("likes", []))
        config["user_persona"]["dislikes"] = analysis_data.get("dislikes", config["user_persona"].get("dislikes", []))
        config["user_persona"]["mood_trends"] = analysis_data.get("mood_trends", "Unknown")
        config["optimal_learning_style"] = analysis_data.get("optimal_learning_style", "Standard")
        
    except Exception as e:
        print(f"[ERROR] Analyst Protocol failed: {e}")
        # --- NEW: Debug Print ---
        # If it fails again, this will print exactly what the LLM tried to say so we can fix it!
        print(f"DEBUG: Raw LLM Output was -> '{analysis_response}'")
        return

    print("\n[2/3] Running Strategist Protocol: Formulating new weekly curriculum...")
    
    old_strategy = config.get("current_weekly_strategy", "")
    struggles = ", ".join(config.get("struggling_points", []))
    likes = ", ".join(config["user_persona"]["likes"])
    
    strategist_prompt = f"""You are the Head Curriculum Director for an AI English Tutor named MochiGo. 
Your job is to write the strict 'Weekly Behavioral Strategy' that MochiGo will follow for the next 7 days.

BACKGROUND DATA:
- The human's favorite topics: {likes}
- The human's learning style: {config['optimal_learning_style']}
- The human's current English struggles: {struggles}
- MochiGo's PREVIOUS Strategy: {old_strategy}

INSTRUCTIONS:
Write a 2-4 sentence instructional paragraph directly commanding MochiGo on how to act. 
Tell MochiGo what tone to use, what topics to weave into the conversation (based on their likes), and what specific English mistakes to passively focus on fixing. 
DO NOT output any extra text. Output ONLY the strategy paragraph.
"""

    try:
        new_strategy = strategist_llm.invoke([HumanMessage(content=strategist_prompt)]).content.strip()
        print(new_strategy)  # Debug print to see the new strategy before saving
        
        # Save old strategy to history for future reference
        if old_strategy:
            history = config.setdefault("strategy_history", [])
            history.append(old_strategy)
            
            # --- NEW: Cap the history at 20 entries to prevent file bloat ---
            if len(history) > 20:
                config["strategy_history"] = history[-20:]
            
        config["current_weekly_strategy"] = new_strategy
        save_config(config)
        
    except Exception as e:
        print(f"[ERROR] Strategist Protocol failed: {e}")
        return
    
if __name__ == "__main__":
    run_sleep_cycle()