from langchain_core.tools import tool
from core.database import get_knowledge_base_collection
from services.ingestion.vector_store import MyCustomVectorStore

@tool
async def search_legal_documents(query: str):
    """Searches the legal knowledge base for relevant document snippets and laws.
    Returns formatted text for the LLM and includes metadata for follow-up links.
    """
    collection = get_knowledge_base_collection()
    vector_store = MyCustomVectorStore(collection_name="knowledge_base")
    
    # Perform similarity search
    results = vector_store.similarity_search(query, k=8)

    
    if not results:
        return "No relevant legal documents found."

    # 1. Format the content for the LLM to read
    # Standardize metadata keys to match pdf_engine.py
    formatted_results = "\n\n".join([
        f"Source: {res.metadata.get('filename')} (Page {res.metadata.get('page')})\nContent: {res.page_content}"
        for res in results
    ])

    # 2. Return a structured response. 
    # LangGraph allows returning a string, but we can embed metadata here if needed.
    return formatted_results 

legal_tools = [search_legal_documents]