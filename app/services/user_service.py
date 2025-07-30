from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.auth import (create_access_token, create_refresh_token, hash_password,
                      verify_password)
from app.models import User, UserProfile
from app.schemas import UserCreate, UserLogin


# Eager-load profile when fetching by email
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(User).options(selectinload(User.profile)).filter(User.email == email)
    )
    return result.scalars().first()


#  Create user + profile, then re-fetch with profile included
async def create_user_with_profile(db: AsyncSession, user_data: UserCreate):
    hashed = hash_password(user_data.password)
    user = User(
        name=user_data.name, email=user_data.email, password=hashed, role=user_data.role
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

    #  Replace db.refresh(user) with re-fetch including profile
    result = await db.execute(
        select(User).options(selectinload(User.profile)).filter(User.id == user.id)
    )
    user = result.scalars().first()
    return user


#  Login with user + profile and return tokens
async def login_user(login_data: UserLogin, db: AsyncSession):
    result = await db.execute(
        select(User)
        .options(selectinload(User.profile))
        .filter(User.email == login_data.email)
    )
    user = result.scalars().first()

    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    profile = user.profile
    return {
        "tokens": {
            "access_token": create_access_token({"sub": user.email}),
            "refresh_token": create_refresh_token({"sub": user.email}),
            "token_type": "bearer",
        }
    }
