from typing import Annotated, Sequence, TypedDict, Union
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    The state of the legal assistant.
    
    - messages: The full list of conversation history.
    - current_context: Any specific legal document text retrieved.
    - user_id: ID of the person asking, to ensure data privacy.
    """
    
    # The 'add_messages' function tells LangGraph to append new 
    # AI/Human messages to the list instead of replacing it.
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # You can add custom fields here to track specific legal metadata
    current_context: str
    user_id: str