import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Header
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from schemas import UserCreateRequest, UserCreateResponse, UserCreate, LoginRequest
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
        errors = [item['loc'][0] for item in error_messages]
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"errorMessage": f"{errors} is a required field."}
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
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"errorMessage": "Server error."}
        )

# 로그인
@router.post("/signin", status_code=status.HTTP_200_OK)
async def signin(request: Request, db: Session = Depends(get_db)):
    try:
        credentials = await request.json()
        credentials = LoginRequest(**credentials)
    except ValidationError as e:
        error_messages = e.errors()
        errors = [item['loc'][0] for item in error_messages]
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"errorMessage": f"{errors} is a required field."}
        )
    
    try:
        user = get_user_by_loginId(db, credentials.loginId)
        if not user or not verify_password(credentials.password, user.password):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"errorMessage": "Login Failed."}
            )
        
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.loginId}, expires_delta=access_token_expires
        )
        refresh_token_expires = timedelta(days=7)
        refresh_token = create_access_token(
            data={"sub": user.loginId}, expires_delta=refresh_token_expires
        )
        
        headers = {
            "access": access_token,
            "refresh": refresh_token
        }
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Login Success."},
            headers=headers
        )
    
    except Exception as e:
        logger.error(f"Error occurred during login: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"errorMessage": "Server error."}
        )
        
# 아이디 중복 확인
@router.get("/check-loginid", status_code=status.HTTP_200_OK)
async def check_loginid(loginid: str = Query(default=None), db: Session = Depends(get_db)):
    if not loginid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"errorMessage": "Userid cannot be null or empty."}
        )

    try:
        db_user = get_user_by_loginId(db, loginid)
        if db_user:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"errorMessage": "Userid is already in use."}
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Userid is available"}
        )
    
    except Exception as e:
        logger.error(f"Error occurred during userid check: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"errorMessage": "Server error."}
        )
        
# access token 재발행
@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(refresh: str = Header(None), db: Session = Depends(get_db)):
    if not refresh:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"errorMessage": "Invalid refresh token"}
        )
    
    try:
        payload = decode_access_token(refresh)
        if payload is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"errorMessage": "Invalid refresh token"}
            )
        
        user = get_user_by_loginId(db, payload["sub"])
        if user is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"errorMessage": "Invalid refresh token"}
            )

        access_token_expires = timedelta(minutes=30)
        new_access_token = create_access_token(
            data={"sub": user.loginId}, expires_delta=access_token_expires
        )
        refresh_token_expires = timedelta(days=7)
        new_refresh_token = create_access_token(
            data={"sub": user.loginId}, expires_delta=refresh_token_expires
        )
        
        headers = {
            "access": new_access_token,
            "refresh": new_refresh_token
        }
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Token reissued successfully"},
            headers=headers
        )
    
    except Exception as e:
        logger.error(f"Error occurred during token refresh: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"errorMessage": "Server error."}
        )

# 로그아웃
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(access: str = Header(None)):
    if not access:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"errorMessage": "Access token is null."}
        )
    
    try:
        payload = decode_access_token(access)
        if payload is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"errorMessage": "Access token has expired"}
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Logout successful."}
        )
    
    except Exception as e:
        logger.error(f"Error occurred during logout: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"errorMessage": "Server error."}
        )