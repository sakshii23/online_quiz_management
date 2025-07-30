from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.schemas import UserCreate, UserLogin
from app.services.auth.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup")
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_async_session)):
    user = await AuthService.signup(user_data, db)
    return {"message": "Signup successful", "user": user}


@router.post("/login")
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_async_session)):
    return await AuthService.login(login_data, db)
