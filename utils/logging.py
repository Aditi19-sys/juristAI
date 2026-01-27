from datetime import datetime, timezone

from core.database import get_database

async def log_token_usage(user_email: str, plan_type: str, tokens: int):
    """Call this function whenever the AI generates a response."""
    db = get_database()
    usage_coll = db["token_usage_logs"]
    
    log_entry = {
        "user_email": user_email,
        "plan_type": plan_type,
        "tokens_used": tokens,
        "timestamp": datetime.now(timezone.utc)
    }
    
    await usage_coll.insert_one(log_entry)