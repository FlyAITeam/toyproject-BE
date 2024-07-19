import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from schemas import UserCreateRequest, UserCreateResponse, UserCreate
from core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from crud import create_user, get_user_by_loginId
from database import get_db

router = APIRouter()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 회원가입 기능
@router.post("/signup", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: Request, db: Session = Depends(get_db)):
    try:
        user = await request.json()
        user = UserCreateRequest(**user)
    except ValidationError as e:
        error_messages = e.errors()
        first_error = error_messages[0]
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"errorMessage": f"{first_error['loc'][0]} is a required field."}
        )
    db_user = get_user_by_loginId(db, user.loginId)
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="loginId is already in use.")
    
    try:
        user_data = UserCreate(
            loginId=user.loginId,
            password=get_password_hash(user.password),
            username=user.name,
            disabilities=user.disabilities
        )
        db_user = create_user(db, user_data)
        
        return UserCreateResponse(
            name=db_user.username,
            message="Registration successful",
            userId=db_user.userId
        )
    except Exception as e:
        logger.error(f"Error occurred while creating user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error.")