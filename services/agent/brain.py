from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver # <--- New Import
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from models.state import AgentState
from services.agent.tools import legal_tools
from langchain_google_genai import ChatGoogleGenerativeAI
import logging 

logger = logging.getLogger(__name__)

# 1. Setup MongoDB checkpointer
# We use a standard MongoClient here for the checkpointer
client = AsyncIOMotorClient(settings.DB_URL)
checkpointer = AsyncMongoDBSaver(client, db_name=settings.DB_NAME, collection_name="checkpoints")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=settings.GEMINI_API_KEY
).bind_tools(legal_tools)

async def call_model(state: AgentState):
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(legal_tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

# 2. Compile with the checkpointer
agent_executor = workflow.compile(checkpointer=checkpointer)