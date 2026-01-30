from pydantic_settings import BaseSettings, SettingsConfigDict
from pymongo import MongoClient
import logging
import os
# Initialize logger for the config module
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Bootstrap Keys (Must be in .env)
    DB_URL: str
    DB_NAME: str
    
    # AI & Service Keys (Can be in .env OR MongoDB)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY") # Default to empty, loaded from DB
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security 
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore" 
    )

    def load_from_mongodb(self):
        """Fetches dynamic settings from the MongoDB settings collection."""
        try:
            client = MongoClient(self.DB_URL)
            db = client[self.DB_NAME]
            # Match the collection name 'settings' from your screenshot
            db_settings = db["settings"].find_one({})
            
            if db_settings:
                # Map MongoDB keys to Pydantic keys
                # Note: your screenshot shows camelCase (geminiApiKey)
                if "geminiApiKey" in db_settings:
                    self.GEMINI_API_KEY = db_settings["geminiApiKey"]
                
                logger.info("✅ Configuration loaded from MongoDB")
            client.close()
        except Exception as e:
            logger.error(f"❌ Failed to load settings from MongoDB: {e}")

settings = Settings()
# Call this immediately to populate the keys
settings.load_from_mongodb()