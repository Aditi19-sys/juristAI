from pymongo import MongoClient  # Import sync client
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from core.config import settings

class MyCustomVectorStore:
    def __init__(self):
        # 1. Use synchronous MongoClient for the Vector Store
        self.client = MongoClient(settings.DB_URL)
        self.db = self.client[settings.DB_NAME]
        self.collection = self.db["knowledge_base"]
        
        # 2. Define your embedding model
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.GEMINI_API_KEY
        )
        
        self.vector_store = MongoDBAtlasVectorSearch(
            collection=self.collection,
            embedding=self.embeddings,
            index_name="default"  # Ensure this matches your MongoDB Atlas index name
        )