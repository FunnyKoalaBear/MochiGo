from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # 'add_messages' ensures LangGraph appends new messages to the list, rather than overwriting it.
    messages: Annotated[list[AnyMessage], add_messages]
    user_level: str 
    struggling_points: list[str]
    next_action: str       # Will hold either "chat" or "rag"
    teaching_topic: str    # Will hold the specific grammar point or lesson to teach
    taught_concepts: dict[str, list[str]]
    weekly_strategy: str