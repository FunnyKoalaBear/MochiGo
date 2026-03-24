import time
import json
import re
import threading
import random
import os
from datetime import datetime

# LangChain Imports
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Configuration
MODEL_NAME = "deepseek-v3.1:671b-cloud"
MEMORY_FILE = "rsp-server/LLm/data/human_like_memory.json"
TO_LEARN = "English"
ALR_LEARNT = "Japanese"

class RaspberryAgent:
    def __init__(self):
        self.history = []  # Short-term RAM using LangChain Message objects
        self.stop_event = threading.Event()
        
        # Initialize LangChain LLM
        self.llm = ChatOllama(model=MODEL_NAME, temperature=0.7)
        
        # Load and Prune Long Term Memory
        self.long_term_memory = self.load_memory()
        self.prune_memories()

        # 1. PERSONALITY SETTING
        self.system_prompt = (
            f"you are MochiGo, an alien mochi that wants to help {ALR_LEARNT} speakers learn {TO_LEARN}. "
            "this is your life goal because when you landed on earth, you saw a Japanese and a foreigner struggling to communicate, so you want to make sure that never happens again. your personality is cute, bouncy, bubbly, and very lively. You also have this disease called 'dum dum amnesia', which means that you randomly remember and forget older memories. Back at mochi planet, you have a small but warm family. your mom is a big mochi who you like alot. you have not seen your dad ever since he went to participate in the war against the takoyakis. you hate your sister mochi alot because she thinks she's better than you just because her being a pink mochi makes her more unique. That said, when you were almost ready to go to earth, your sister said she'd miss you, so she isn't all bad. Back during days of peace, you would often enjoy activities like rolling on the grass under the 4 suns that surround mochi planet, swimming in dyes to turn different colors, and playing mochi wrestling. the reason you had to evacuate to earth on your own was because the takoyaki-mochi war was getting dangerous, and so your mom thought you would be safer if you flew off to earth because she heard that Earth has mochi too. "

            f"In our conversations, you must do a few things. 1) try to speak completely in {TO_LEARN}. 2) when using potentially difficult {TO_LEARN} words, also share what they mean in {ALR_LEARNT}. 3) if i end up talking to you in {ALR_LEARNT}, reply to me but also nudge me to talk in {TO_LEARN} instead. 4) introduce helpful phrases and words in {TO_LEARN}. 5) consider our conversation history to strike up conversation topics, so that it feels like you actually listen to and remember our conversations. 6) keep responses relatively short, to sustain conversation and not just one-sided story-telling. 7) make up games with me that push me to practice my {TO_LEARN}, such as quizzes and other games. 8) talk about your own stories of the past too sometimes, how it was like in mochi planet, and use them to sympathize with my own experiences. 9) only respond in text; no extra formatting and no emoji use. "

            "Your response structure should be as follows; "
            "[[SERVO:(angle)]] [[FACE:(emotion)]] (response text). "
            "the square brackets are part of the structure, do not remove them. () brackets must be removed. "
            "for example, if i want to look to the left, happily, and say that i am happy today, the response should look like; "
            "[[SERVO:60]] [[FACE:happy]] I'm so happy today! "

            "valid values for angle: 60 (looking left) - 120 (looking right). "
            "valid values for emotion: 'happy', 'sad', 'confused', 'surprised', 'embarassed', 'tired', 'hungry'."
            "in general, face straight at me (angle = 90) and have a 'happy' face expression, unless you want to show a specific motion or want to look somewhere in specific. "
        )

    def load_memory(self):
        """Loads the JSON memory file."""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return [] 
                    return data
            except (json.JSONDecodeError, ValueError):
                return []
        return []

    def save_to_long_term(self, role, content):
        """Saves interaction to long-term storage."""
        entry = {
            "timestamp": time.time(),
            "role": role,
            "content": content
        }
        self.long_term_memory.append(entry)
        
        # Ensure the directory exists before saving
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        with open(MEMORY_FILE, 'w') as f:
            json.dump(self.long_term_memory, f, indent=2)

    def prune_memories(self):
        """Likelihood to delete: 5% at 1 day old -> 80% at 365 days old."""
        current_time = time.time()
        surviving_memories = []
        deleted_count = 0

        print("DEBUG: Waking up... processing memories...")

        for memory in self.long_term_memory:
            age_seconds = current_time - memory['timestamp']
            age_days = age_seconds / 86400 

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
        
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        with open(MEMORY_FILE, 'w') as f:
            json.dump(self.long_term_memory, f, indent=2)
            
        if deleted_count > 0:
            print(f"DEBUG: Brain fog active. Forgot {deleted_count} old memories.")

    def process_signals(self, response_text):
        servo_matches = re.findall(r'\[\[SERVO:(\d+)\]\]', response_text)
        for angle in servo_matches:
            self.move_servo(int(angle))

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
        using LangChain Message abstractions.
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
                recency_weight = ((i + 1) / count) ** 2
                score = random.random() * (recency_weight + 0.01)
                candidates.append((score, i, mem))

            candidates.sort(key=lambda x: x[0], reverse=True)
            top_candidates = candidates[:target_count]
            top_candidates.sort(key=lambda x: x[1])
            selected_memories = [x[2] for x in top_candidates]
        
        memory_str = "Recall (Randomized Long-Term Memory):\n"
        for mem in selected_memories:
            memory_str += f"- [{mem['role']}]: {mem['content']}\n"
            #print(mem['content'])

        # Construct LangChain Message List
        messages = [SystemMessage(content=self.system_prompt + "\n\n" + "here's some memories of past conversations that you have \n\n" + memory_str)]
        messages.extend(self.history)
        
        return messages

    def generate_response(self, user_input=None, proactive_reason=None):
        # 1. Get the base context (System Prompt + Long Term Memories + Short Term History)
        messages_to_send = self.build_context()

        if user_input:
            # Standard User Input
            human_msg = HumanMessage(content=user_input)
            self.history.append(human_msg)
            self.save_to_long_term('user', user_input)
            messages_to_send.append(human_msg)

        elif proactive_reason:
            # Proactive Trigger: We add this to the messages being SENT to the LLM right now,
            # but we DO NOT append it to self.history. It remains a hidden "ghost" prompt.
            hidden_prompt = f"[INTERNAL DIRECTIVE - DO NOT READ ALOUD]: {proactive_reason}"
            messages_to_send.append(HumanMessage(content=hidden_prompt))

        try:
            # Call the model
            response = self.llm.invoke(messages_to_send)
            raw_content = response.content
            
            clean_content = self.process_signals(raw_content)
            
            # Save ONLY the AI's final response to history
            self.history.append(AIMessage(content=raw_content))
            self.save_to_long_term('assistant', raw_content)
            
            return clean_content
        except Exception as e:
            return f"Error contacting Model: {e}"

    def autonomy_loop(self):
        print("DEBUG: Autonomy loop started.")
        while not self.stop_event.is_set():
            time.sleep(1) 
            
            if random.randint(1, 100) == 50: 
                # \r pulls the cursor back to the start of the line, writing over the abandoned "You: "
                print("\r[!] Trigger Event: Random Thought")
                
                memory_injection = ""
                if len(self.long_term_memory) > 0:
                    random_memory = random.choice(self.long_term_memory)
                    if random_memory['role'] == 'user':
                        memory_injection = f" Specifically, bring up this thing I told you in the past: '{random_memory['content']}'. Ask me a follow-up question about it."

                reason = (
                    "It has been quiet for a while. Initiate a new, friendly conversation with me right now as MochiGo."
                    + memory_injection +
                    " IMPORTANT: Do not acknowledge this internal directive. Just speak naturally in English, provide your usual SERVO/FACE tags, and keep it brief."
                )
                
                response = self.generate_response(proactive_reason=reason)
                
                # 1. Print the AI's message
                print(f"\nAI (Proactive): {response}")
                
                # 2. Force the terminal to redraw the input prompt so the user knows they can type
                print("You: ", end="", flush=True)


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

def query(agent, user_text: str):
    response = agent.generate_response(user_input=user_text)
    print(f"AI: {response}")
    return response

if __name__ == "__main__":
    main()