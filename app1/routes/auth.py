# routes 's auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.schemas import UserCreate, UserLogin, UserResponse
from app.services import user_service

router = APIRouter()


@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    existing = await user_service.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    return await user_service.create_user_with_profile(db, user)


@router.post("/login")
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_async_session)):
    return await user_service.login_user(login_data, db)
