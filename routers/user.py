from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import User
from crud import get_user
from database import get_db
from core.security import decode_access_token

router = APIRouter()

def get_current_user(token: str = Depends(decode_access_token), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user(db, user_id=payload["sub"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
