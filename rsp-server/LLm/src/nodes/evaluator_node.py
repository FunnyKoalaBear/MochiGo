import json
from core.state import AgentState
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, get_buffer_string

# 1. SPEED UP: Use a tiny, fast model just for routing!
# (Make sure you run `ollama pull llama3.2` or `qwen2.5:3b` in your terminal)
FAST_ROUTING_MODEL = "gpt-oss:20b-cloud" 

# 2. SPEED UP: Force native JSON mode so it doesn't waste tokens on markdown
eval_llm = ChatOllama(model=FAST_ROUTING_MODEL, temperature=0.0, format="json")

def evaluator_node(state: AgentState):
    """Lightning-fast semantic router."""
    messages = state["messages"]
    
    route = "chat"
    topic = "NONE"

    last_msg_content = messages[-1].content if messages else ""
    if "[INTERNAL" in last_msg_content or "[TEACHING" in last_msg_content:
        # Keep struggling points intact while returning early
        return {"next_action": "chat", "teaching_topic": "NONE"}

    # Grab the last 3 messages for context
    recent_msgs = messages[-3:]
    clean_msgs = [msg for msg in recent_msgs if not msg.content.startswith("[")]
    recent_history = get_buffer_string(clean_msgs)

    # --- NEW: Stricter Prompt ---
    prompt = f"""Analyze this English tutoring conversation:

    {recent_history}

    Focusing on the User's final reply, output ONLY JSON with these exact 2 keys:
    
    "route": Choose "dictionary" if the user explicitly asks for the meaning, definition, or translation of a specific word (e.g., "what does X mean?"). Choose "chat" if the user is answering a simple question, playing a game, making small talk, or sharing a personal story. Choose "rag" if the user asks to learn something new like grammar points or formal greetings, examples of things like sentence structure or tenses, or makes a severe mistake that requires a textbook lesson.
    "topic": If "route" is "rag", define a short question to find its answer or relevant context from the textbooks/novels. If "route" is "dictionary", write the EXACT SINGLE WORD they are asking about. Else, write "NONE".

    JSON Format Example:
    {{"route": "rag", "topic": "what is past participle"}}
    {{"route": "chat", "topic": "NONE"}}
    """

    try:
        response = eval_llm.invoke([HumanMessage(content=prompt)]).content.strip()
        data = json.loads(response)
        
        # 1. Get the raw route and make it lowercase
        raw_route = str(data.get("route", "chat")).lower()
        
        # 2. SANITIZE: Force the LLM's answer into one of our 3 strict paths
        if "dict" in raw_route:
            route = "dictionary"
        elif "rag" in raw_route:
            route = "rag"
        else:
            route = "chat"
            
        topic = data.get("topic", "NONE")
        
        print(f"[BACKGROUND EVALUATOR] Decision -> Route: {route.upper()} | Topic: {topic}")

    except Exception as e:
        print(f"DEBUG: Evaluator logic failed -> {e}")

    # Notice we no longer return struggling_points here. The Chat Node handles it now.
    return {
        "next_action": route, 
        "teaching_topic": topic
    }