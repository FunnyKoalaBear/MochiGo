from core.state import AgentState
from memory.vector_course import KnowledgeBase
from langchain_core.messages import SystemMessage

kb = KnowledgeBase()

def dict_rag_node(state: AgentState):
    """Fetches dictionary definitions and commands MochiGo to explain them."""
    
    word_to_define = state.get("teaching_topic", "")
    #print(f"DEBUG: Dictionary Node looking up word: '{word_to_define}'")
            
    definition_text = kb.retrieve_dictionary_word(word_to_define)
    #print(f"DEBUG: Dictionary Node retrieved items: '{definition_text}'\n")
    
    instruction = (
        f"[SYSTEM OVERRIDE]: MochiGo, the user wants to know what '{word_to_define}' means. "
        f"Explain it to them simply using ONLY the dictionary reference below. "
        f"If the exact word is NOT in the reference material, politely say your dictionary "
        f"doesn't have it, and provide your own definition instead.\n\n"
        f"CRITICAL: You MUST end your response with the hidden tag [[TAUGHT_DEF: {word_to_define}]].\n\n"
        f"Dictionary Reference:\n{definition_text}"
    )
    
    return {"messages": [SystemMessage(content=instruction)]}