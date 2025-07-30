from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Union
from app.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models import User, UserProfile
from app.schemas import UserCreate, UserLogin
from app.services.auth.queries import (
    get_user_by_email
)


class AuthService:

    @staticmethod
    async def signup(user_data: UserCreate, db: AsyncSession) -> User:
        existing_user = await get_user_by_email(user_data.email, db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists.",
            )

        hashed_pw = hash_password(user_data.password)
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=hashed_pw,
            role=user_data.role,
        )
        db.add(user)
        await db.flush()

        if user_data.profile:
            profile = UserProfile(
                user_id=user.id,
                contact_no=user_data.profile.contact_no,
                profile_image=user_data.profile.profile_image,
                dob=user_data.profile.dob,
                gender=user_data.profile.gender,
                batch=user_data.profile.batch,
                designation=user_data.profile.designation,
            )
            db.add(profile)

        await db.commit()

        # Re-fetch with profile
        return await get_user_by_email(user.email, db)

    @staticmethod
    async def login(login_data: UserLogin, db: AsyncSession) -> dict:
        user = await get_user_by_email(login_data.email, db)

        if not user or not verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
            )

        return {
            "tokens": {
                "access_token": create_access_token({"sub": user.email}),
                "refresh_token": create_refresh_token({"sub": user.email}),
                "token_type": "bearer",
            }
        }
