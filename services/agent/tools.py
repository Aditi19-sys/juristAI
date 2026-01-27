from langchain_core.tools import tool
from core.database import get_knowledge_base_collection
from services.ingestion.vector_store import MyCustomVectorStore

@tool
async def search_legal_documents(query: str):
    """Searches the legal knowledge base for relevant document snippets and laws."""
    collection = get_knowledge_base_collection()
    vector_store = MyCustomVectorStore(collection)
    
    # Perform similarity search
    results = await vector_store.similarity_search(query, k=3)
    
    formatted_results = "\n\n".join([
        f"Source: {res.metadata.get('filename')} (Page {res.metadata.get('page')})\nContent: {res.page_content}"
        for res in results
    ])
    return formatted_results if formatted_results else "No relevant legal documents found."

legal_tools = [search_legal_documents]