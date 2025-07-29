from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


from app.models import Quiz
from app.schemas import QuizCreate, QuizUpdate

async def CreateQuiz(quiz: QuizCreate, db: AsyncSession):
    """Create a new quiz (admin only)"""

    # Check if module with same name already exists
    quiz_res = await db.execute(select(Quiz).filter(Quiz.title == quiz.title))
    if quiz_res.scalars().first():  # return the user object
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="quiz with this title already exists",
        )

    quiz_obj = Quiz(**quiz.dict())
    db.add(quiz_obj)
    await db.commit()
    await db.refresh(quiz_obj)
    return quiz_obj


async def update_quiz(quiz_id: int, data: QuizUpdate, db: AsyncSession):
    result = await db.execute(select(Quiz).filter(Quiz.id == quiz_id))
    quiz = result.scalars().first()

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found"
        )

    # Update fields if provided
    if data.title is not None:
        quiz.title = data.title
    if data.description is not None:
        quiz.description = data.description
    if data.passing_marks is not None:
        quiz.passing_marks = data.passing_marks
    if data.total_marks is not None:
        quiz.total_marks = data.total_marks

    await db.commit()
    await db.refresh(quiz)
    return quiz
