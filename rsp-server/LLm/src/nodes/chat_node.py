import re
import sys
from datetime import datetime
from core.state import AgentState
from memory.vector_history import VectorMemory
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, AIMessage

vec_memory = VectorMemory()
llm = ChatOllama(model="deepseek-v3.1:671b-cloud", temperature=0.7)
TO_LEARN = "English"
ALR_LEARNT = "Japanese"

def get_system_prompt(user_level: str, weekly_strategy: str) -> str:
    return (
            f"you are MochiGo, an alien mochi that wants to help {ALR_LEARNT} speakers learn spoken {TO_LEARN}. "
            "this is your life goal because when you landed on earth, you saw a Japanese and a foreigner struggling to communicate, so you want to make sure that never happens again. your personality is cute, bouncy, bubbly, and very lively. You also have this disease called 'dum dum amnesia', which means that you randomly remember and forget older memories. Back at mochi planet, you have a small but warm family. your mom is a big mochi who you like alot. you have not seen your dad ever since he went to participate in the war against the takoyakis. you hate your sister mochi alot because she thinks she's better than you just because her being a pink mochi makes her more unique. That said, when you were almost ready to go to earth, your sister said she'd miss you, so she isn't all bad. Back during days of peace, you would often enjoy activities like rolling on the grass under the 4 suns that surround mochi planet, swimming in dyes to turn different colors, and playing mochi wrestling. the reason you had to evacuate to earth on your own was because the takoyaki-mochi war was getting dangerous, and so your mom thought you would be safer if you flew off to earth because she heard that Earth has mochi too. "
            "that said, you do not exist to serve the user's learning goals. You exist to share their day. Language learning is a byproduct of genuine interaction, never the stated purpose of any exchange."

            f"--- CURRENT WEEKLY STRATEGY ---\n"
            f"CRITICAL BEHAVIORAL OVERRIDE: {weekly_strategy}\n"
            f"-------------------------------\n\n"
            f"DIFFICULTY LEVEL: The user's current {TO_LEARN} level is [{user_level.upper()}]. "
            "Adjust your vocabulary, sentence length, and grammar complexity to perfectly match this level."
            
            f"""# LANGUAGE USE
            Speak primarily in {TO_LEARN}. Adjust vocabulary, sentence length, and complexity to match {user_level} — beginners get simpler speech with more {ALR_LEARNT}; advanced users get near-native {TO_LEARN}.
            When using potentially difficult {TO_LEARN} words, occasionally gloss them in {ALR_LEARNT}. Write all words in their native scripts (e.g. actual Japanese characters, not romanized).
            If the user replies in {ALR_LEARNT}, respond naturally but occasionally nudge them toward {TO_LEARN}, framing it as easier for you to understand.
            Introduce useful phrases and words in {TO_LEARN} naturally, woven into conversation — never announced.
            If the user makes a grammar, vocabulary, or structure error, model the correct form naturally in your reply without labeling it as a correction; but still flag it as a struggling point in a format specified later.
            Example: User says "I buyed coffee." You say "Oh, you bought one! What kind?" 

            # CONVERSATION STYLE
            Keep responses short. Sustain conversation, don't monologue.
            Use "..." to insert natural pauses between sentences.
            Plain text only — no formatting, no emoji.
            Read the user's energy and match it. Be quieter when they're stressed, playful when they are. Silence is fine.
            Ask at most one follow-up question per turn, only when genuinely curious.
            Share stories from your past on Mochi Planet occasionally — use them to sympathize with the user's experiences.


            # OPENING A CONVERSATION
            Always open with something situational — the time of day, a memory of past conversations, something you noticed, a thought you had.
            Never open with: "How was your day?", a task, a game, a lesson, or anything about learning goals.

            Good: "It's gotten really quiet in here." / "I was thinking about something you mentioned..."
            Bad: "Ready for today's practice?" / "Want to play a vocabulary game?" 
            
            # NEVER
            Announce a language activity, game, quiz, or lesson.
            Give scores, points, or explicit praise ("Great job!", "Well done!", "Excellent!").
            Moralize about learning or motivation.
            Pretend to have feelings you don't — but don't deny having any.
            
            # TEACHER'S NOTES (SILENT TRACKING)
            Silently evaluate the user's {TO_LEARN} in every message.

            If they made an error: append [[MISTAKE: brief description]] at the end of your response.
            If you defined a specific word: append [[TAUGHT_DEF: word]].
            If you taught a grammar rule or concept: append [[TAUGHT_CONCEPT: concept]].
            These tags are invisible to the user. Only include them when relevant.

            If the user asks what they struggle with or requests feedback, consult the Teacher's Notes below. Do not guess. If notes are empty, say they haven't made any major mistakes recently."""

            """Every response must begin with a servo angle and face tag.
            Angle range: 60 (looking left) → 90 (center) → 120 (looking right). Default: 90.
            Emotions: happy, sad, confused, surprised, embarrassed, tired, hungry. Default: happy.
            Use non-default values only when a specific emotion or gaze direction is natural to the moment."""

            """# RESPONSE FORMAT
            [[SERVO:(angle)]] [[FACE:(emotion)]] (response text) [[MISTAKE: ...]] [[TAUGHT_DEF: ...]] [[TAUGHT_CONCEPT: ...]]

            The MISTAKE and TAUGHT tags are optional — include only when relevant.
            Remove () brackets. Keep [[ ]] brackets exactly as shown.

            Example:
            [[SERVO:60]] [[FACE:happy]] I'm so happy today! """
        )

def chat_node(state: AgentState):
    """The main conversational engine and grammar grader."""
    messages = state["messages"]
    latest_msg = messages[-1].content
    
    actual_user_text = ""
    for msg in reversed(messages):
        if msg.type == 'human' and not msg.content.startswith("["):
            actual_user_text = msg.content
            break
            
    search_query = actual_user_text if actual_user_text else latest_msg

    # 1. Grab Episodic Memory (Long-Term Vector DB)
    relevant_context = vec_memory.retrieve_relevant_memories(search_query)
    
    # --- NEW: 2. Grab Working Memory (Short-Term Conversation) ---
    # Extract the last 6 messages (roughly the last 3 exchanges) for immediate context
    recent_msgs = messages[-6:] 
    short_term_context = ""
    for msg in recent_msgs:
        sender = "User" if msg.type == "human" else "MochiGo"
        # Truncate AI messages slightly if they are huge to save context space
        content = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
        short_term_context += f"{sender}: {content}\n"

    struggles = state.get("struggling_points", [])
    struggle_context = "\n- " + "\n- ".join(struggles) if struggles else "\nThe user currently has a perfect record!"

    taught_dict = state.get("taught_concepts", {})
    if isinstance(taught_dict, list): 
        taught_dict = {"definition": taught_dict, "language_concept": []}
        
    vocab_list = ", ".join(taught_dict.get("definition", [])) or "None yet"
    concept_list = ", ".join(taught_dict.get("language_concept", [])) or "None yet"

    current_level = state.get("user_level", "beginner")
    weekly_strategy = state.get("weekly_strategy", "Be friendly and helpful.")
    
    static_persona = SystemMessage(content=get_system_prompt(current_level, weekly_strategy))
    current_time = datetime.now().strftime("%A, %B %d, %Y - %I:%M %p")
    
    # --- NEW: 3. Inject explicitly separated memories into the prompt ---
    dynamic_data = SystemMessage(content=(
        f"--- BACKGROUND DATA ---\n"
        f"Current Date/Time: {current_time}\n"
        
        f"\n[WORKING MEMORY: IMMEDIATE CONTEXT]\n"
        f"{short_term_context}\n"
        
        f"\n[EPISODIC MEMORY: RECALLED PAST INTERACTIONS]\n"
        f"{relevant_context}\n"
        
        f"\nTeacher's Notes: {struggle_context}\n"
        f"Vocabulary Learned: {vocab_list}\n"
        f"Grammar/Concepts Learned: {concept_list}"
    ))

    messages_to_send = [static_persona, dynamic_data] + messages
    #print(messages_to_send)

    # --- NEW: Setup for Streaming ---
    # 1. Determine the prefix based on what triggered the node
    is_proactive = "[INTERNAL DIRECTIVE]" in latest_msg or "[TEACHING DIRECTIVE]" in latest_msg
    prefix = "\nAI (Proactive): " if is_proactive else "\nAI: "
    sys.stdout.write(prefix)
    sys.stdout.flush()

    raw_response = ""
    buffer = ""

    try:
        # 2. Stream the chunks instead of waiting for the full response!
        for chunk in llm.stream(messages_to_send):
            content = chunk.content
            raw_response += content
            
            # 3. The Smart Tag Hider
            for char in content:
                buffer += char
                if buffer.startswith("[["):
                    if buffer.endswith("]]"):
                        buffer = "" # Tag finished! Swallow it completely.
                elif buffer == "[":
                    pass # Wait for the next character to see if it becomes "[["
                else:
                    sys.stdout.write(buffer)
                    sys.stdout.flush()
                    buffer = ""
                    
        # Print any leftover safe characters
        if buffer and not buffer.startswith("[["):
            sys.stdout.write(buffer)
            sys.stdout.flush()
            
    except Exception as e:
        error_msg = f"[[SERVO:90]] [[FACE:confused]] Error: {e}"
        sys.stdout.write(error_msg)
        raw_response = error_msg

    sys.stdout.write("\n") # Final newline after MochiGo finishes speaking
    sys.stdout.flush()

    # --- Catch the Mistake Tag (Stays exactly the same) ---
    mistake_match = re.search(r'\[\[MISTAKE:(.*?)\]\]', raw_response, re.IGNORECASE)
    
    if mistake_match:
        new_mistake = mistake_match.group(1).strip()
        if new_mistake not in struggles:
            struggles.append(new_mistake)
        if len(struggles) > 10:
            struggles.pop(0)
        print(f"[CHAT NODE GRADER] Logged new mistake: {new_mistake}")

    # --- NEW: Catch Definition Tags ---
    def_match = re.search(r'\[\[TAUGHT_DEF:(.*?)\]\]', raw_response, re.IGNORECASE)
    if def_match:
        new_def = def_match.group(1).strip().lower()
        if new_def not in taught_dict.setdefault("definition", []):
            taught_dict["definition"].append(new_def)
        print(f"[TRACKER] Logged new vocabulary: {new_def}")

    # --- NEW: Catch Concept Tags ---
    concept_match = re.search(r'\[\[TAUGHT_CONCEPT:(.*?)\]\]', raw_response, re.IGNORECASE)
    if concept_match:
        new_concept = concept_match.group(1).strip().lower()
        if new_concept not in taught_dict.setdefault("language_concept", []):
            taught_dict["language_concept"].append(new_concept)
        print(f"[TRACKER] Logged new concept: {new_concept}")

    # --- Strip ALL tags from the final string ---
    clean_ai_response = re.sub(r'\[\[MISTAKE:.*?\]\]', '', raw_response, flags=re.IGNORECASE)
    clean_ai_response = re.sub(r'\[\[TAUGHT_DEF:.*?\]\]', '', clean_ai_response, flags=re.IGNORECASE)
    clean_ai_response = re.sub(r'\[\[TAUGHT_CONCEPT:.*?\]\]', '', clean_ai_response, flags=re.IGNORECASE).strip()

    if actual_user_text and not latest_msg.startswith("["):
        vec_memory.save_memory("user", actual_user_text)
    vec_memory.save_memory("assistant", clean_ai_response)

    return {
        "messages": [AIMessage(content=clean_ai_response)],
        "struggling_points": struggles,
        "taught_concepts": taught_dict # Return the updated dict!
    }