from langgraph.graph import StateGraph, START, END
from core.state import AgentState

# Import our new separate nodes
from nodes.evaluator_node import evaluator_node
from nodes.rag_node import rag_node
from nodes.chat_node import chat_node, vec_memory

from nodes.evaluator_node import evaluator_node
from nodes.rag_node import rag_node
from nodes.dict_rag_node import dict_rag_node  # NEW IMPORT
from nodes.chat_node import chat_node, vec_memory

def input_router(state: AgentState):
    last_msg = state["messages"][-1].content
    if "[TEACHING DIRECTIVE]" in last_msg: return "rag"
    elif "[INTERNAL DIRECTIVE]" in last_msg: return "chat"
    else: return "evaluator"

def eval_router(state: AgentState):
    # Now it can return "chat", "rag", OR "dictionary"
    return state.get("next_action", "chat")

# --- BUILD THE LANGGRAPH ---
builder = StateGraph(AgentState)

builder.add_node("evaluator", evaluator_node)
builder.add_node("rag", rag_node)
builder.add_node("dict_rag", dict_rag_node) # NEW NODE
builder.add_node("chat", chat_node)

builder.add_conditional_edges(START, input_router, {
    "rag": "rag", 
    "chat": "chat", 
    "evaluator": "evaluator"
})

builder.add_conditional_edges("evaluator", eval_router, {
    "rag": "rag",
    "dictionary": "dict_rag", # NEW ROUTE
    "chat": "chat"
})

builder.add_edge("rag", "chat")
builder.add_edge("dict_rag", "chat") # Route from dictionary back to chat
builder.add_edge("chat", END)

mochigo_app = builder.compile()