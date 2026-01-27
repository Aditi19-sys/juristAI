from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from core.security import verify_password, create_access_token
from core.database import get_users_collection

router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    users_collection = get_users_collection()
    
    # In MongoDB, we use email as the unique identifier
    # Add a max_time_ms to force a timeout if the DB is unreachable
    user = await users_collection.find_one(
            {"email": form_data.username}
        )
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}