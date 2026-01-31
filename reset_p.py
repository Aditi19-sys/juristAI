import asyncio
from datetime import datetime
from core.database import connect_to_mongo, close_mongo_connection, get_users_collection
from core.security import get_password_hash

EMAIL = "shiv@eoxysit.com"
NEW_PASSWORD = "Test@1234"

async def main():
    # 🔑 Initialize DB (same as FastAPI startup)
    await connect_to_mongo()

    users = get_users_collection()
    result = await users.update_one(
        {"email": EMAIL},
        {"$set": {"hashed_password": get_password_hash(NEW_PASSWORD)}}
    )

    if result.matched_count:
        print("✅ Password reset successful")
    else:
        print("❌ User not found")

    # 🧹 Clean shutdown
    await close_mongo_connection()

asyncio.run(main())
