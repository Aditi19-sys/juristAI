from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.database import connect_to_mongo, close_mongo_connection
from services.ingestion.vector_store import MyCustomVectorStore
# 1. Added 'management' to the import list
from api.endpoints import iam, auth, assistant, management 

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB
    await connect_to_mongo()
    print("✅ Database Connected")
    # Initialize Vector Store
    app.state.v_store = MyCustomVectorStore()
    print("✅ Vector Store Initialized")
    
    yield
    
    # Shutdown: Close connections
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

# Authentication & Identity
app.include_router(iam.router, prefix="/api/iam", tags=["Authentication"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# Assistant Logic
app.include_router(assistant.router, prefix="/api/assistant", tags=["Assistant"])

# 2. Add the Management/Admin routes here
app.include_router(management.router, prefix="/api", tags=["Admin Management"])

if __name__ == "__main__":
    import uvicorn
    # 3. Fixed the host/port for local development
    uvicorn.run(app, host="127.0.0.1", port=8000)