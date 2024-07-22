from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import User
from crud import get_user_by_loginId
from database import get_db
from core.security import decode_access_token
from fastapi import APIRouter, Depends, HTTPException, status, Request

router = APIRouter()

#@router.post("/check-userid", status_code=status.HTTP_200_OK)
#async def checkUserId(request: Request, db: Session = Depends(get_db)):
    