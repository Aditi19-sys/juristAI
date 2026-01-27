from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from pymongo.server_api import ServerApi

client = None
database = None

async def connect_to_mongo():
    global client, database
    try:
        client = AsyncIOMotorClient(settings.DB_URL, server_api=ServerApi('1'))
        database = client[settings.DB_NAME]
        await client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    global client
    if client:
        client.close()

def get_database(): return database

# Existing Collections
def get_users_collection(): return database.users
def get_chats_collection(): return database.chats
def get_documents_collection(): return database.documents
def get_knowledge_base_collection(): return database.knowledge_base

# New Collections for Admin Dashboard (from your screenshot)
def get_token_usage_collection(): return database.token_usage
def get_subscriptions_collection(): return database.subscriptions
def get_plans_collection(): return database.plans
def get_messages_collection(): return database.messages
def get_settings_collection(): return database.settings
def get_embedding_vector(): return database.embedding_vector