from sqlalchemy import select, func, and_, update, exists,distinct  # Added exists here
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import datetime
from app.models import StudentQuizAttempt, QuizAnswer, Question, Quiz, Module, StudentModuleStatus
from app.schemas import QuizAttemptCreate
from sqlalchemy.orm import selectinload
from fpdf import FPDF
from pathlib import Path
import os
from datetime import datetime


async def update_module_status(
    user_id: int, 
    module_id: int, 
    is_passed: bool,
    db: AsyncSession
) -> StudentModuleStatus:
    """Updates module status for a user"""
    status = await db.scalar(
        select(StudentModuleStatus)
        .where(StudentModuleStatus.user_id == user_id)
        .where(StudentModuleStatus.module_id == module_id)
    )
    
    if not status:
        status = StudentModuleStatus(
            user_id=user_id,
            module_id=module_id,
            is_unlocked=is_passed,
            is_completed=is_passed,
            unlocked_on=datetime.utcnow() if is_passed else None
        )
        db.add(status)
    elif is_passed:
        if not status.is_unlocked:
            status.is_unlocked = True
            status.unlocked_on = datetime.utcnow()
        if not status.is_completed:
            status.is_completed = True
    
    await db.commit()
    await db.refresh(status)
    return status



async def unlock_next_module(user_id: int, module_id: int, db: AsyncSession):
    """Unlock next module for a user if they have completed the current one"""
    current_module = await db.scalar(
        select(Module)
        .where(Module.id == module_id)
    )

    next_module = await db.scalar(  
        select(Module)
        .where(Module.id == current_module.next)
    ).first()
    
    if next_module:
        status = await db.scalar(
            select(StudentModuleStatus)
            .where(StudentModuleStatus.user_id == user_id)
            .where(StudentModuleStatus.module_id == next_module.id)
        )
        
        if not status:
            new_status = StudentModuleStatus(
                user_id=user_id,
                module_id=next_module.id,
                is_unlocked=True,
                is_completed=False,
                unlocked_on=datetime.utcnow()
            )
            db.add(new_status)
        else:
            status.is_unlocked = True
            status.unlocked_on = datetime.utcnow()
            status.is_completed = False
            
        await db.commit()
        await db.refresh(new_status)
        return new_status
    return None

async def update_module_status(
    user_id: int, 
    module_id: int, 
    is_passed: bool,
    db: AsyncSession
) -> StudentModuleStatus:
    """Updates module status for a user"""
    status = await db.scalar(
        select(StudentModuleStatus)
        .where(StudentModuleStatus.user_id == user_id)
        .where(StudentModuleStatus.module_id == module_id)
    )
    
    if not status:
        status = StudentModuleStatus(
            user_id=user_id,
            module_id=module_id,
            is_unlocked=is_passed,
            is_completed=is_passed,
            unlocked_on=datetime.utcnow() if is_passed else None
        )
        db.add(status)
    elif is_passed:
        if not status.is_completed:
            status.is_completed = True

        await unlock_next_module(user_id, module_id, db)
    
    await db.commit()
    await db.refresh(status)
    return status




async def submit_quiz_attempt_service(
    user_id: int, 
    attempt_data: QuizAttemptCreate, 
    db: AsyncSession
):
    try:
        # Check attempt limits
        attempts = await db.scalars(
            select(StudentQuizAttempt)
            .where(StudentQuizAttempt.user_id == user_id)
            .where(StudentQuizAttempt.quiz_id == attempt_data.quiz_id)
            .order_by(StudentQuizAttempt.submitted_at.desc())
        )
        attempts_list = attempts.all()
        
        if len(attempts_list) >= 3:
            if any(attempt.is_passed for attempt in attempts_list[:3]):
                raise HTTPException(400, "You already passed this quiz (max 3 attempts)")
            raise HTTPException(400, "Maximum 3 attempts reached")

        # Get quiz with module
        quiz = await db.scalar(
            select(Quiz)
            .where(Quiz.id == attempt_data.quiz_id)
            .options(selectinload(Quiz.module))
        )
        if not quiz or not quiz.module:
            raise HTTPException(404, "Quiz not found or not associated with module")

        # Create fresh attempt
        attempt = StudentQuizAttempt(
            user_id=user_id,
            quiz_id=attempt_data.quiz_id,
            total_marks=0,
            obtained_marks=0,
            is_passed=False
        )
        db.add(attempt)
        await db.flush()

        # Process answers
        questions = await db.scalars(
            select(Question)
            .where(Question.id.in_([a.question_id for a in attempt_data.answers]))
        )
        question_map = {q.id: q for q in questions}

        for answer in attempt_data.answers:
            question = question_map.get(answer.question_id)
            if not question:
                raise HTTPException(404, f"Question {answer.question_id} not found")
            
            if answer.selected_option not in question.options:
                raise HTTPException(400, f"Invalid option for question {question.id}")

            is_correct = (answer.selected_option == question.correct_answer)
            attempt.total_marks += question.marks
            attempt.obtained_marks += question.marks if is_correct else 0

            db.add(QuizAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                selected_option=answer.selected_option,
                is_correct=is_correct
            ))

        # Determine pass/fail (80% requirement)
        attempt.is_passed = (attempt.obtained_marks / attempt.total_marks) >= 0.8

        # Update module status if passed
        module_status = None
        if attempt.is_passed:
            module_status = await update_module_status(
                user_id=user_id,
                module_id=quiz.module.id,
                is_passed=True,
                db=db
            )

        await db.commit()
        await db.refresh(attempt)
        
        return {
            "attempt": attempt,
            "module_status": module_status,
            "passed": attempt.is_passed,
            "score": f"{attempt.obtained_marks}/{attempt.total_marks}",
            "percentage": f"{(attempt.obtained_marks/attempt.total_marks)*100:.2f}%"
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, f"Error processing quiz: {str(e)}")



