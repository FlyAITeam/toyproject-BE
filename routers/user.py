import logging
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import ValidationError
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from core.security import decode_access_token, create_access_token
from crud import get_user_by_loginId, update_user_disabilities, get_user_logs
from database import get_db
from datetime import timedelta
from schemas import NameUpdateRequest, DisabilityUpdateRequest

router = APIRouter()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 회원 정보 조회
@router.get("/user", status_code=status.HTTP_200_OK)
async def get_user_info(access: str = Header(None), refresh: str = Header(None), db: Session = Depends(get_db)):
    if not access:
        # 액세스 토큰이 없는 경우
        if not refresh:
            # 리프레시 토큰도 없는 경우
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"errorMessage": "access 토큰과 refresh 토큰이 없습니다."}
            )
        else:
            # 리프레시 토큰이 있는 경우
            new_access_token = refresh_access_token(refresh, db)
            if new_access_token is None:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"errorMessage": "refresh 토큰이 유효하지 않습니다."}
                )
            access = new_access_token  # 새로운 액세스 토큰으로 대체

    try:
        payload = decode_access_token(access)
        if payload is None:
            # 액세스 토큰이 만료된 경우
            if not refresh:
                # 리프레시 토큰이 없는 경우
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"errorMessage": "access 토큰이 만료되었고 refresh 토큰이 없습니다."}
                )
            else:
                # 리프레시 토큰이 있는 경우
                new_access_token = refresh_access_token(refresh, db)
                if new_access_token is None:
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"errorMessage": "refresh 토큰이 유효하지 않습니다."}
                    )
                access = new_access_token  # 새로운 액세스 토큰으로 대체
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=user_info,
                    headers={"access": new_access_token}
                )

        user = get_user_by_loginId(db, payload["sub"])
        if user is None:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"errorMessage": "access 토큰이 유효하지 않습니다."}
            )

        user_info = {
            "name": user.username,
            "userId": user.loginId,
            "disabilities": [disability.obstacle for disability in user.disabilities]
        }
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=user_info
        )

    except Exception as e:
        logger.error(f"Error occurred during user info retrieval: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"errorMessage": "Server error."}
        )

def refresh_access_token(refresh_token: str, db: Session):
    try:
        payload = decode_access_token(refresh_token)
        if payload is None:
            return None

        user = get_user_by_loginId(db, payload["sub"])
        if user is None:
            return None

        access_token_expires = timedelta(minutes=30)
        new_access_token = create_access_token(
            data={"sub": user.loginId}, expires_delta=access_token_expires
        )

        return new_access_token

    except Exception as e:
        logger.error(f"Error occurred during access token refresh: {e}")
        return None
    
# 사용자 이름 변경
@router.put("/user/name", status_code=status.HTTP_200_OK)
async def update_user_name(request: NameUpdateRequest, access: str = Header(None), db: Session = Depends(get_db)):
    if not access:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"errorMessage": "Access token is null."}
        )
    
    try:
        payload = decode_access_token(access)
        if payload is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"errorMessage": "Access token has expired"}
            )

        user = get_user_by_loginId(db, payload["sub"])
        if user is None:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"errorMessage": "Invalid access token"}
            )
        
        if not request.name:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"errorMessage": "Name cannot be null or empty"}
            )
        
        # 이름 업데이트
        user.username = request.name
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Name updated successfully"}
        )
    
    except Exception as e:
        logger.error(f"Error occurred while updating name: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"errorMessage": "Server error."}
        )
        
# disability 변경
@router.put("/user/disability", status_code=status.HTTP_200_OK)
async def update_disabilities(request: DisabilityUpdateRequest, access: str = Header(None), db: Session = Depends(get_db)):
    if not access:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"errorMessage": "Access token is null."}
        )
    
    try:
        payload = decode_access_token(access)
        if payload is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"errorMessage": "Access token has expired"}
            )

        user = get_user_by_loginId(db, payload["sub"])
        if user is None:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"errorMessage": "Invalid access token"}
            )
        
        # 장애 목록 업데이트
        update_user_disabilities(db, user.userId, request.disabilities)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Disabilities updated successfully"}
        )
    
    except ValidationError as e:
        error_messages = e.errors()
        errors = [item['loc'][0] for item in error_messages]
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"errorMessage": f"{errors} is a required field."}
        )
    
    except Exception as e:
        logger.error(f"Error occurred while updating disabilities: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"errorMessage": "Server error."}
        )
        
@router.get("/user/log", status_code=status.HTTP_200_OK)
async def get_user_info(access: str = Header(None), refresh: str = Header(None), db: Session = Depends(get_db)):
    if not access:
        # 액세스 토큰이 없는 경우
        if not refresh:
            # 리프레시 토큰도 없는 경우
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"errorMessage": "access 토큰과 refresh 토큰이 없습니다."}
            )
        else:
            # 리프레시 토큰이 있는 경우
            new_access_token = refresh_access_token(refresh, db)
            if new_access_token is None:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"errorMessage": "refresh 토큰이 유효하지 않습니다."}
                )
            access = new_access_token  # 새로운 액세스 토큰으로 대체

    try:
        payload = decode_access_token(access)
        if payload is None:
            # 액세스 토큰이 만료된 경우
            if not refresh:
                # 리프레시 토큰이 없는 경우
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"errorMessage": "access 토큰이 만료되었고 refresh 토큰이 없습니다."}
                )
            else:
                # 리프레시 토큰이 있는 경우
                new_access_token = refresh_access_token(refresh, db)
                if new_access_token is None:
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"errorMessage": "refresh 토큰이 유효하지 않습니다."}
                    )
                access = new_access_token  # 새로운 액세스 토큰으로 대체
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    headers={"access": new_access_token}
                )
        user = get_user_by_loginId(db, payload["sub"])
        if user is None:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"errorMessage": "access 토큰이 유효하지 않습니다."}
            )
        logger.debug("login success")
        # 사용자 로그 조회
        logs = get_user_logs(db, user.userId)
        log_data = []
        for log in logs:
            log_entry = {
                "imagePath": log.logImage.path,
                "imageCloth": log.logReform.cloth
            }
            log_data.append(log_entry)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"logs": log_data}
        )

    except Exception as e:
        logger.error(f"Error occurred during user log retrieval: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"errorMessage": "Server error."}
        )