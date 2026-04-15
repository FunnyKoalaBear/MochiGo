import threading
import time
import random
import re
from langchain_core.messages import HumanMessage
from core.graph import mochigo_app
from core.config import load_config, save_config, save_chat_history
from core.onboarding import run_onboarding

class RaspberryHardware:
    """Handles the physical body of MochiGo (Signals and Loops)"""
    def __init__(self):
        self.stop_event = threading.Event()
        self.last_interaction_time = time.time()
        
        # --- Load Persistent Config ---
        self.config = load_config()
        
        # Initialize the LangGraph state
        self.current_state = {
            "messages": [], 
            "user_level": self.config.get("user_level", "beginner"), 
            "struggling_points": self.config.get("struggling_points", []), # NEW: Load from config
            "taught_concepts": self.config.get("taught_concepts", {"definition": [], "language_concept": []})
        }

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
        pass # print(f" >>> SERVO: {angle}")

    def set_screen_emotion(self, emotion):
        pass # print(f" >>> FACE: {emotion}")

    def autonomy_loop(self):
        """The background heartbeat for proactive thoughts."""
        print("DEBUG: Autonomy loop started. Waiting for 60 seconds of silence...")
        while not self.stop_event.is_set():
            time.sleep(1) 
            
            # Check the stopwatch. If 60 seconds haven't passed, skip the rest of the loop.
            if time.time() - self.last_interaction_time < 60:
                continue
            
            # If we made it here, it has been at least 1 minute of silence!
            # 1 in 100 chance to trigger per second (adjust to 1 in 10 if you want it to happen faster after the 1 min mark)
            if random.randint(1, 100) == 50: 
                
                # 50/50 split between a Random Chat and a Teaching Moment
                if random.choice([True, False]):
                    print("\r[!] Trigger Event: Teaching Moment")
                    hidden_command = HumanMessage(content="[TEACHING DIRECTIVE]: Bring up a topic about some specific english language learning point (like grammar, sentence structure, formal english etc) using rag. Choose a random topic yourself.")
                else:
                    print("\r[!] Trigger Event: Random Thought")
                    hidden_command = HumanMessage(content="[INTERNAL DIRECTIVE]: It has been quiet. Initiate a new, brief conversation.")
                
                # Run the graph
                result = mochigo_app.invoke({
                    "messages": self.current_state["messages"] + [hidden_command],
                    "user_level": self.current_state["user_level"],
                    "struggling_points": self.current_state["struggling_points"],
                    "taught_concepts": self.current_state.get("taught_concepts", self.config.get("taught_concepts", {})),
                    "weekly_strategy": self.config.get("current_weekly_strategy", "Be friendly and helpful.")
                })
                
                # Update our session state with the graph's output
                self.current_state = result
                
                # Save both concepts and struggles to permanent config
                self.config["taught_concepts"] = result.get("taught_concepts", self.config.get("taught_concepts", {}))
                self.config["struggling_points"] = result.get("struggling_points", self.config.get("struggling_points", [])) # NEW
                save_config(self.config)

                save_chat_history(self.current_state["messages"])
                
                raw_ai_text = result["messages"][-1].content
                clean_ai_text = self.process_signals(raw_ai_text)
                                
                # NEW: Reset the stopwatch after MochiGo speaks proactively!
                self.last_interaction_time = time.time()
                
                print("You: ", end="", flush=True)

def main():
    body = RaspberryHardware()
    
    # --- NEW: Run Onboarding if First Boot ---
    if body.config.get("is_first_boot", True):
        body.config = run_onboarding(body.config)
        # Make sure the graph state gets the updated level!
        body.current_state["user_level"] = body.config["user_level"]
    
    # Start autonomy
    t = threading.Thread(target=body.autonomy_loop)
    t.start()

    print("System Ready (LangGraph + VectorDB Active). Type 'quit' to exit.")
    
    try:
        while True:
            user_text = input("You: ")
            
            # NEW: Reset the stopwatch the moment you hit Enter
            body.last_interaction_time = time.time()
            
            if user_text.lower() in ["quit", "exit"]:
                break
            
            if user_text.lower() == "new session":
                body.current_state["messages"] = []
                print("--- Short Term Memory Wiped ---")
                continue
            
            # 1. Package the user input into a LangChain message
            input_message = HumanMessage(content=user_text)
            
            # 2. Pass the current state to the LangGraph application
            result = mochigo_app.invoke({
                "messages": body.current_state["messages"] + [input_message],
                "user_level": body.current_state["user_level"],
                "struggling_points": body.current_state["struggling_points"],
                "taught_concepts": body.current_state.get("taught_concepts", body.config.get("taught_concepts", {})),
                "weekly_strategy": body.config.get("current_weekly_strategy", "Be friendly and helpful.")
            })
            
            # 3. Save the updated state
            body.current_state = result
            
            # Save both concepts and struggles to permanent config
            body.config["taught_concepts"] = result.get("taught_concepts", body.config.get("taught_concepts", {}))
            body.config["struggling_points"] = result.get("struggling_points", body.config.get("struggling_points", [])) # NEW
            save_config(body.config)

            save_chat_history(body.current_state["messages"])
            
            # 4. Extract and process the AI's response
            raw_ai_text = result["messages"][-1].content
            clean_ai_text = body.process_signals(raw_ai_text)
                        
            # NEW: Reset the stopwatch right after the AI finishes replying to you
            body.last_interaction_time = time.time()

    except KeyboardInterrupt:
        pass
    finally:
        body.stop_event.set()
        t.join()
        print("System shutdown.")

if __name__ == "__main__":
    main()