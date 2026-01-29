from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from core.config import settings

class MyCustomVectorStore:
    def __init__(self, collection_name: str = "knowledge_base"):
        self.client = MongoClient(settings.DB_URL)
        self.db = self.client[settings.DB_NAME]
        self.collection = self.db[collection_name]
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=settings.GEMINI_API_KEY,
            output_dimensionality=3072,
            task_type="retrieval_query" 
        )
        
        self.vector_store = MongoDBAtlasVectorSearch(
            collection=self.collection,
            embedding=self.embeddings,
            index_name="vector_index",
            text_key="text"
        )

    def similarity_search(self, query: str, k: int = 20):
        # num_candidates is CRITICAL for 3072 dimensions
        return self.vector_store.similarity_search(
            query, 
            k=k,
            num_candidates=150 
        )

    def similarity_search_with_score(self, query: str, k: int = 5):
        return self.vector_store.similarity_search_with_score(
            query, 
            k=k,
            num_candidates=100
        )