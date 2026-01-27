from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    DB_URL: str
    DB_NAME: str

    # AI
    GEMINI_API_KEY: str

    #redis 
    REDIS_URL: str

    # Security 
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Any other keys in your .env must be here
    # Example: if you have X_API_KEY in .env, add it here:
    X_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore"  # <--- ADD THIS LINE to stop the error for extra keys
    )

settings = Settings()