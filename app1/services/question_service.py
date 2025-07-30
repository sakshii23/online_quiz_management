from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Question
from app.schemas import QuestionCreate, QuestionUpdate


async def create_question(data: QuestionCreate, db: AsyncSession):
    print("Creating question with data:", data)
    result = await db.execute(select(Question).filter(Question.text == data.text))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="question with this quiz id already exists",
        )
    quiz_obj = Question(**data.dict())
    db.add(quiz_obj)
    await db.commit()
    await db.refresh(quiz_obj)
    return quiz_obj


async def update_question(question_id: int, data: QuestionUpdate, db: AsyncSession):
    result = await db.execute(select(Question).filter(Question.id == question_id))
    question = result.scalars().first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Store the original quiz_id before updates
    original_quiz_id = question.quiz_id

    # Update only the fields that are provided in the request
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(question, field, value)

    await db.commit()
    await db.refresh(question)

    # Construct the response ensuring quiz_id is included
    response_data = {
        "id": question.id,
        "quiz_id": original_quiz_id,
        "text": question.text,
        "marks": question.marks,
        "options": question.options,
        "correct_answer": question.correct_answer,
    }

    return response_data
