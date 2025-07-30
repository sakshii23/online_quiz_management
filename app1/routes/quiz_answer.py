from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.schemas import QuizAttemptCreate, QuizAttemptResponse
from app.services.quiz_answer_service import submit_quiz_attempt_service
from app.auth import get_current_user
router = APIRouter(prefix="/attempts", tags=["Quiz Attempts"])

@router.post("/", response_model=QuizAttemptResponse)
async def submit_attempt(
    attempt_data: QuizAttemptCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user=Depends(get_current_user)
):
    return await submit_quiz_attempt_service(current_user.id, attempt_data, db)