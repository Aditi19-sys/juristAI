from langchain_core.tools import tool
from services.ingestion.vector_store import MyCustomVectorStore
import logging
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)

# Initialize vector store once at module load (singleton pattern)
_vector_store = None

def get_vector_store():
    """Returns a cached instance of the vector store to avoid recreating it on every call."""
    global _vector_store
    if _vector_store is None:
        _vector_store = MyCustomVectorStore(collection_name="knowledge_base")
    return _vector_store

@tool
async def search_legal_documents(query: str):
    """Searches the legal knowledge base for relevant document snippets and laws.
    Returns formatted text for the LLM and includes metadata for follow-up links.
    """
    try:
        vector_store = get_vector_store()
        
        # Perform similarity search
        results = vector_store.similarity_search(query, k=8)
        
        if not results:
            return "No relevant legal documents found."

        # Format the content for the LLM to read
        # Standardize metadata keys to match pdf_engine.py
        formatted_results = "\n\n".join([
            f"Source: {res.metadata.get('filename')} (Page {res.metadata.get('page')})\nContent: {res.page_content}"
            for res in results
        ])

        return formatted_results
    
    except Exception as e:
        logger.error(f"Error searching legal documents: {e}")
        return f"Error searching knowledge base: {str(e)}"

legal_tools = [search_legal_documents]