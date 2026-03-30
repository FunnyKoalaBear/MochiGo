import random
from core.state import AgentState
from memory.vector_course import KnowledgeBase
from langchain_core.messages import SystemMessage

kb = KnowledgeBase()

def rag_node(state: AgentState):
    """Fetches textbook material, with new reinforcement logic."""
    topic = state.get("teaching_topic", "NONE")
    
    # NEW: If proactive, decide whether to fix a struggle or reinforce a past concept
    if topic == "NONE" or topic == "":
        struggles = state.get("struggling_points", [])
        
        # Safely grab the dictionary
        taught_dict = state.get("taught_concepts", {})
        past_concepts = taught_dict.get("language_concept", [])
        
        # 50/50 chance to either fix a mistake or review a past lesson
        if struggles and past_concepts:
            if random.random() > 0.5:
                topic = random.choice(past_concepts)
                print(f"DEBUG: RAG Node chosen to REINFORCE past concept: '{topic}'")
            else:
                topic = random.choice(struggles)
                print(f"DEBUG: RAG Node chosen to FIX struggle: '{topic}'")
        elif struggles:
            topic = random.choice(struggles)
        elif past_concepts:
            topic = random.choice(past_concepts)
        else:
            topic = "basic conversational english"
            
    print(f"DEBUG: RAG Node opening textbook to chapter: '{topic}'")
            
    lesson = kb.retrieve_course_topic(topic)
    
    instruction = (
        f"[SYSTEM OVERRIDE]: MochiGo, initiate a teaching moment! "
        f"Teach the user about '{topic}' using ONLY the reference material provided below. "
        f"CRITICAL: You MUST end your response with the hidden tag [[TAUGHT_CONCEPT: {topic}]].\n\n"
        f"Reference Material:\n{lesson}\n\n"
        f"After teaching the concept, ask them a quick practice question about it."
    )
    
    return {"messages": [SystemMessage(content=instruction)]}