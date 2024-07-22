from fastapi import APIRouter
from . import auth, user

router = APIRouter()
router.include_router(auth.router, tags=["auth"])
router.include_router(user.router, tags=["users"])