from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import admin_only
from app.database import get_async_session
from app.schemas import QuizCreate, QuizResponse, QuizUpdate
from app.services.quiz_service import CreateQuiz, update_quiz

router = APIRouter()


from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import admin_only
from app.database import get_async_session
from app.schemas import QuizCreate, QuizResponse, QuizUpdate
from app.services.quiz_service import CreateQuiz, update_quiz

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])

@router.post("/", response_model=QuizResponse)
async def create_quiz(
    data: QuizCreate,
    db: AsyncSession = Depends(get_async_session),
    admin=Depends(admin_only),
):
    return await CreateQuiz(data, db)


@router.put("/{quiz_id}", response_model=QuizResponse)
async def edit_quiz(
    quiz_id: int = Path(..., description="ID of the module to update"),
    data: QuizUpdate = Depends(),
    db: AsyncSession = Depends(get_async_session),
    _=Depends(admin_only),
):
    return await update_quiz(quiz_id, data, db)
