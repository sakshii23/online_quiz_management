from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import admin_only
from app.database import get_async_session
from app.schemas import QuestionCreate, QuestionResponse, QuestionUpdate
from app.services.question_service import create_question, update_question

router = APIRouter()


@router.post("/", response_model=QuestionResponse)
async def create_question_api(
    data: QuestionCreate,
    db: AsyncSession = Depends(get_async_session),
    _=Depends(admin_only),
):
    return await create_question(data, db)


@router.put("/{question_id}", response_model=QuestionResponse)
async def edit_question_api(
    question_id: int = Path(...),
    data: QuestionUpdate = Depends(),
    db: AsyncSession = Depends(get_async_session),
    _=Depends(admin_only),
):
    return await update_question(question_id, data, db)
