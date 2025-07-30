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


async def unlock_next_module(user_id: int, module_id: int, db: AsyncSession):
    """Unlock next module for a user if they have completed the current one"""
    current_module = await db.scalar(
        select(Module)
        .where(Module.id == module_id)
    )

    next_module = await db.scalar(  
        select(Module)
        .where(Module.order == current_module.order + 1)  # Assuming modules are ordered by 'order' field
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
        .where(and_(StudentModuleStatus.user_id == user_id, StudentModuleStatus.module_id == module_id)
    )
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

# async def submit_quiz_attempt_service(user_id: int, attempt_data: QuizAttemptCreate, db: AsyncSession):
#     # 1. Check attempt limit
#     attempt_count = await db.scalar(
#         select(func.count(StudentQuizAttempt.id))
#         .where(StudentQuizAttempt.user_id == user_id)
#         .where(StudentQuizAttempt.quiz_id == attempt_data.quiz_id)
#     )
    
#     if attempt_count >= 3:
#         passed = await db.scalar(
#             select(StudentQuizAttempt.is_passed)
#             .where(StudentQuizAttempt.user_id == user_id)
#             .where(StudentQuizAttempt.quiz_id == attempt_data.quiz_id)
#             .order_by(StudentQuizAttempt.obtained_marks.desc())
#             .limit(1)
#         )
#         if passed:
#             raise HTTPException(400, "You already passed this quiz")
#         raise HTTPException(400, "Maximum 3 attempts reached")

#     # 2. Create new attempt
#     attempt = StudentQuizAttempt(
#         user_id=user_id,
#         quiz_id=attempt_data.quiz_id,
#         total_marks=0,
#         obtained_marks=0,
#         is_passed=False
#     )
#     db.add(attempt)
#     await db.flush()

#     # 3. Process answers
#     questions = await db.scalars(
#         select(Question)
#         .where(Question.id.in_([a.question_id for a in attempt_data.answers]))
#     )
#     question_map = {q.id: q for q in questions}

#     for answer in attempt_data.answers:
#         question = question_map.get(answer.question_id)
#         if not question:
#             raise HTTPException(404, f"Question {answer.question_id} not found")
        
#         if answer.selected_option not in question.options:
#             raise HTTPException(400, f"Invalid option for question {question.id}")

#         is_correct = (answer.selected_option == question.correct_answer)
#         attempt.total_marks += question.marks
#         attempt.obtained_marks += question.marks if is_correct else 0

#         db.add(QuizAnswer(
#             attempt_id=attempt.id,
#             question_id=question.id,
#             selected_option=answer.selected_option,
#             is_correct=is_correct
#         ))

#     # 4. Determine pass/fail
#     attempt.is_passed = (attempt.obtained_marks >= 0.8 * attempt.total_marks)
    
    
#     await db.commit()
#     await db.refresh(attempt)

#     # 5. Always update module status (pass or fail)
#     status_update = await handle_module_status(
#         user_id=user_id,
#         quiz_id=attempt_data.quiz_id,
#         is_passed=attempt.is_passed,
#         db=db
#     )

#     return attempt









# async def generate_quiz_result_pdf(attempt: StudentQuizAttempt) -> str:
#     """Generate a PDF with quiz results using fpdf2 and return the file path"""
#     try:
#         # Create PDF object
#         pdf = FPDF()
#         pdf.add_page()
        
#         # Set font for the entire document
#         pdf.set_font("Arial", size=12)
        
#         # Add title
#         pdf.set_font("Arial", style='B', size=16)
#         pdf.cell(200, 10, txt="Quiz Result Summary", ln=1, align="C")
#         pdf.ln(10)
        
#         # Add attempt metadata
#         pdf.set_font("Arial", size=12)
#         pdf.cell(200, 10, txt=f"Attempt ID: {attempt.id}", ln=1)
#         pdf.cell(200, 10, txt=f"User ID: {attempt.user_id}", ln=1)
#         pdf.cell(200, 10, txt=f"Quiz ID: {attempt.quiz_id}", ln=1)
#         pdf.cell(200, 10, txt=f"Submitted at: {attempt.submitted_at}", ln=1)
#         pdf.ln(15)
        
#         # Create results table header
#         pdf.set_font("Arial", style='B', size=12)
#         pdf.cell(60, 10, "Metric", border=1, align='C')
#         pdf.cell(60, 10, "Value", border=1, align='C', ln=1)
        
#         # Add table rows
#         pdf.set_font("Arial", size=12)
#         metrics = [
#             ("Total Marks", str(attempt.total_marks)),
#             ("Obtained Marks", str(attempt.obtained_marks)),
#             ("Passing Percentage", "80%"),
#             ("Your Percentage", f"{(attempt.obtained_marks/attempt.total_marks)*100:.2f}%"),
#             ("Result", "PASSED" if attempt.is_passed else "FAILED")
#         ]
        
#         for metric, value in metrics:
#             pdf.cell(60, 10, metric, border=1)
#             pdf.cell(60, 10, value, border=1, ln=1)
        
#         # Add some spacing
#         pdf.ln(15)
        
#         # Add final remarks
#         pdf.set_font("Arial", style='I', size=10)
#         if attempt.is_passed:
#             pdf.cell(200, 10, txt="Congratulations! You have passed this quiz.", ln=1)
#         else:
#             pdf.cell(200, 10, txt="Keep practicing! You can try again.", ln=1)
        
#         # Create storage directory if it doesn't exist
#         pdf_dir = Path("quiz_results")
#         pdf_dir.mkdir(exist_ok=True, mode=0o755)
        
#         # Generate filename
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"quiz_result_{attempt.user_id}_{attempt.id}_{timestamp}.pdf"
#         filepath = pdf_dir / filename
        
#         # Output PDF file
#         pdf.output(filepath)
        
#         return str(filepath)
        
#     except Exception as e:
#         print(f"Error generating PDF: {str(e)}")
#         return None
