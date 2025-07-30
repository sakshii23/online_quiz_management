# app/queries/auth_queries.py

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_
from app.models import User


async def get_user_by_email(email: str, db):
    return await db.execute(
        select(User).options(selectinload(User.profile)).filter(User.email == email)
    )


async def get_user_by_id(user_id: int, db):
    return await db.execute(
        select(User).options(selectinload(User.profile)).filter(User.id == user_id)
    )


async def get_user_for_login(email: str, db):
    return await db.execute(
        select(User).options(selectinload(User.profile)).filter(User.email == email)
    )
