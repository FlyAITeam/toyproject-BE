from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from schemas import UserCreate, User
from core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from crud import create_user, get_user_by_loginId
from database import get_db

router = APIRouter()

@router.post("/signup", response_model=User)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_loginId(db, user.loginId)
    if db_user:
        raise HTTPException(status_code=400, detail="Login ID already registered")
    user.password = get_password_hash(user.password)
    return create_user(db, user)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_loginId(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.loginId}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token-refresh")
def refresh_token(token: str):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    new_token = create_access_token(data={"sub": payload["sub"]})
    return {"access_token": new_token, "token_type": "bearer"}

@router.get("/check-username")
def check_username(loginId: str, db: Session = Depends(get_db)):
    user = get_user_by_loginId(db, loginId)
    if user:
        return {"is_available": False}
    return {"is_available": True}

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}
