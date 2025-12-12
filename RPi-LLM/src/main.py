import ollama
import time
import json
import re
import threading
import random
import os
from datetime import datetime

# Configuration
MODEL_NAME = "gpt-oss:120b-cloud"
MEMORY_FILE = "data\human_like_memory.json"

class RaspberryAgent:
    def __init__(self):
        self.history = []  # Short-term RAM (Session only)
        self.stop_event = threading.Event()
        
        # Load and Prune Long Term Memory
        self.long_term_memory = self.load_memory()
        self.prune_memories() # Run the "forgetting" algorithm on startup

        # 1. PERSONALITY SETTING
        self.system_prompt = (
            "You are a helpful, lively, and cute english-learning desk alien called MochiGo. "
            "You are NOT a language model. you are a living mysterious being. "
            "talk like a child, in a cute tone and grammar. "
            "Besides control responses, do not use any extra formatting or emojis. "
            "If I speak in japanese, answer me but also nudge me into trying to talk in english instead. "
            "You have access to hardware controls. "
            "To look from side to side, output: [[SERVO:angle]] (e.g., [[SERVO:90]]). "
            "To change your screen face, output: [[FACE:emotion]] (e.g., [[FACE:happy]]). "
            "Keep responses concise."
        )

    def load_memory(self):
        """Loads the JSON memory file. Handles empty or corrupt files."""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r') as f:
                    data = json.load(f)
                    # Ensure backward compatibility: if old memory was a dict, convert to list
                    if isinstance(data, dict):
                        return [] 
                    return data
            except (json.JSONDecodeError, ValueError):
                return []
        return []

    def save_to_long_term(self, role, content):
        """Saves every interaction to long-term storage with a timestamp."""
        entry = {
            "timestamp": time.time(),
            "role": role,
            "content": content
        }
        self.long_term_memory.append(entry)
        
        with open(MEMORY_FILE, 'w') as f:
            json.dump(self.long_term_memory, f, indent=2)

    def prune_memories(self):
        """
        Likelihood to delete: 5% at 1 day old -> 80% at 365 days old.
        """
        current_time = time.time()
        surviving_memories = []
        deleted_count = 0

        print("DEBUG: Waking up... processing memories...")

        for memory in self.long_term_memory:
            age_seconds = current_time - memory['timestamp']
            age_days = age_seconds / 86400 

            # Linear probability calculation
            if age_days < 1:
                prob_delete = 0.0
            else:
                prob_delete = 0.05 + (0.00206 * (age_days - 1))
            
            prob_delete = min(prob_delete, 0.90)

            if random.random() < prob_delete:
                deleted_count += 1
            else:
                surviving_memories.append(memory)

        self.long_term_memory = surviving_memories
        
        with open(MEMORY_FILE, 'w') as f:
            json.dump(self.long_term_memory, f, indent=2)
            
        if deleted_count > 0:
            print(f"DEBUG: Brain fog active. Forgot {deleted_count} old memories.")

    # 2. PARALLEL SIGNAL PARSING
    def process_signals(self, response_text):
        # Regex to find [[SERVO:xxx]]
        servo_matches = re.findall(r'\[\[SERVO:(\d+)\]\]', response_text)
        for angle in servo_matches:
            self.move_servo(int(angle))

        # Regex to find [[FACE:xxx]]
        face_matches = re.findall(r'\[\[FACE:(\w+)\]\]', response_text)
        for emotion in face_matches:
            self.set_screen_emotion(emotion)

        clean_text = re.sub(r'\[\[.*?\]\]', '', response_text).strip()
        return clean_text

    def move_servo(self, angle):
        print(f" >>> HARDWARE ACTION: Moving Servo to {angle} degrees")

    def set_screen_emotion(self, emotion):
        print(f" >>> HARDWARE ACTION: Displaying '{emotion}' face")

    def build_context(self):
        """
        Combines System Prompt + (Weighted Selection of Long Term Memories) + Short Term History
        """
        all_memories = self.long_term_memory
        count = len(all_memories)
        target_count = 20
        selected_memories = []

        if count <= target_count:
            selected_memories = all_memories
        else:
            candidates = []
            for i, mem in enumerate(all_memories):
                # Recency Bias: ((i+1)/total)^2
                recency_weight = ((i + 1) / count) ** 2
                # Random score modified by weight
                score = random.random() * (recency_weight + 0.01)
                candidates.append((score, i, mem))

            # Sort by score (descending) to pick winners
            candidates.sort(key=lambda x: x[0], reverse=True)
            top_candidates = candidates[:target_count]

            # Sort back by index (ascending) to restore timeline
            top_candidates.sort(key=lambda x: x[1])
            selected_memories = [x[2] for x in top_candidates]
        
        # Create a string representation of the selected memories
        memory_str = "Recall (Randomized Long-Term Memory):\n"
        for mem in selected_memories:
            memory_str += f"- [{mem['role']}]: {mem['content']}\n"
            print(f"\nhistory is: "+mem['content'])

        # Construct the final message list
        # We concatenate strings here (system_prompt + memory_str) which is safe
        messages = [{'role': 'system', 'content': self.system_prompt + "\n\n" + memory_str}]
        
        # We extend the list here (messages list + history list) which is safe
        messages.extend(self.history)
        
        return messages

    def generate_response(self, user_input=None, proactive_reason=None):
        if user_input:
            self.history.append({'role': 'user', 'content': user_input})
            self.save_to_long_term('user', user_input)

        elif proactive_reason:
            prompt = f"(Internal System Event: {proactive_reason}. Initiate conversation based on this.)"
            self.history.append({'role': 'system', 'content': prompt})

        try:
            response = ollama.chat(model=MODEL_NAME, messages=self.build_context())
            raw_content = response['message']['content']
            
            clean_content = self.process_signals(raw_content)
            
            self.history.append({'role': 'assistant', 'content': raw_content})
            self.save_to_long_term('assistant', raw_content)
            
            return clean_content
        except Exception as e:
            # This prints the exact error if something goes wrong
            return f"Error contacting Ollama: {e}"

    def autonomy_loop(self):
        print("DEBUG: Autonomy loop started.")
        while not self.stop_event.is_set():
            time.sleep(1) 
            if random.randint(1, 1000) == 500: 
                print("\n[!] Trigger Event: Random Thought")
                response = self.generate_response(proactive_reason="You just thought of something interesting about robots.")
                print(f"\nAI (Proactive): {response}")

def main():
    agent = RaspberryAgent()
    
    t = threading.Thread(target=agent.autonomy_loop)
    t.start()

    print("System Ready. Type 'quit' to exit.")
    print("Type 'new session' to clear short-term memory.")
    
    try:
        while True:
            user_text = input("You: ")
            
            if user_text.lower() in ["quit", "exit"]:
                break
            
            if user_text.lower() == "new session":
                agent.history = []
                print("--- Short Term Memory Wiped (New Session Started) ---")
                continue
            
            response = agent.generate_response(user_input=user_text)
            print(f"AI: {response}")

    except KeyboardInterrupt:
        pass
    finally:
        agent.stop_event.set()
        t.join()
        print("System shutdown.")

if __name__ == "__main__":
    main()