from fastapi import APIRouter, HTTPException
from models.domain import ChatRequest, ChatResponse
from services.agent.brain import agent_executor
from langchain_core.messages import HumanMessage
from datetime import datetime, timezone
import uuid
import logging
import traceback
# Use the logger we configured earlier
logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    try:
        # 1. Ensure we have a thread_id (either from user or generate new)
        thread_id = request.chat_id or str(uuid.uuid4())
        logger.info(f"Chat request received. Thread: {thread_id}")
        # 2. Configure the run with the thread_id
        config = {"configurable": {"thread_id": thread_id}}
        
        inputs = {"messages": [HumanMessage(content=request.message)]}
        
        # 3. ainvoke now automatically loads/saves history based on thread_id
        result = await agent_executor.ainvoke(inputs, config=config)
        
        final_answer = result["messages"][-1].content
        logger.info(f"Successfully generated response for Thread: {thread_id}")

        return ChatResponse(
            message=final_answer,
            chat_id=thread_id,
            timestamp=datetime.now(timezone.utc)
        )
    # api/endpoints/assistant.py
    except Exception as e:
        # This will now tell you if it's a Location error or an Invalid Model error
        logger.error(f"Gemini API Error: {str(e)}") 
        raise HTTPException(status_code=500, detail=f"AI Provider Error: {str(e)}")