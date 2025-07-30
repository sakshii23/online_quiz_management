from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_async_session
from app.schemas import AnswerSubmission
from app.services.quiz.quiz_attempt_service import QuizAttemptService
from app.services.quiz.quiz_submission_service import QuizService

router = APIRouter(prefix="/quiz-attempts", tags=["Quiz Attempts"])


@router.post("/answer")
async def submit_quiz_answer(
        payload: AnswerSubmission,
        db: AsyncSession = Depends(get_async_session),
        user_id: int = 1  # Replace with real auth
):
    service = QuizAttemptService(db)

    try:
        result = await service.answer_question(
            user_id=user_id,
            question_id=payload.question_id,
            student_answer=payload.answer,
            quiz_id=payload.quiz_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/submit/")
async def submit_quiz(
    student_id: int,
    quiz_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    service = QuizService(db)
    try:
        result = await service.submit_quiz(student_id=student_id, quiz_id=quiz_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))