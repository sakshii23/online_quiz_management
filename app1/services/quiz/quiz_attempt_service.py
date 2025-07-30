from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, func
from datetime import datetime

from app.models import (
    StudentQuizAttempt, QuizAnswer, Question
)


class QuizAttemptService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def answer_question(
            self, user_id: int, question_id: int, student_answer: str, quiz_id: int = None
    ):
        # Step 1: Get Question
        question = await self.db.scalar(
            select(Question).where(Question.id == question_id)
        )
        if not question:
            raise ValueError("Invalid question ID.")

        quiz_id = quiz_id or question.quiz_id

        # Step 2: Get or create active attempt
        attempt = await self.db.scalar(
            select(StudentQuizAttempt).where(
                and_(
                    StudentQuizAttempt.user_id == user_id,
                    StudentQuizAttempt.quiz_id == quiz_id,
                    StudentQuizAttempt.submitted_at == None  # Not yet finalized
                )
            )
        )

        if not attempt:
            attempt = StudentQuizAttempt(
                user_id=user_id,
                quiz_id=quiz_id,
                total_marks=question.quiz.total_marks,  # optional
                obtained_marks=0,
                is_passed=False,
            )
            self.db.add(attempt)
            await self.db.flush()  # To get attempt.id

        # Step 3: Check if already answered
        quiz_answer = await self.db.scalar(
            select(QuizAnswer).where(
                and_(
                    QuizAnswer.attempt_id == attempt.id,
                    QuizAnswer.question_id == question_id
                )
            )
        )

        # Step 4: Check correctness
        is_correct = question.correct_answer.strip().lower() == student_answer.strip().lower()

        if quiz_answer:
            # Update existing answer
            quiz_answer.selected_option = student_answer
            quiz_answer.is_correct = is_correct
        else:
            # Create new answer
            quiz_answer = QuizAnswer(
                attempt_id=attempt.id,
                question_id=question_id,
                selected_option=student_answer,
                is_correct=is_correct
            )
            self.db.add(quiz_answer)

        await self.db.flush()

        # Step 5: Recompute obtained marks (sum of all correct answers)
        total = await self.db.scalar(
            select(func.coalesce(func.sum(Question.marks), 0))
            .join(QuizAnswer, QuizAnswer.question_id == Question.id)
            .where(
                and_(
                    QuizAnswer.attempt_id == attempt.id,
                    QuizAnswer.is_correct == True
                )
            )
        )
        attempt.obtained_marks = total or 0

        await self.db.commit()

        return {
            "attempt_id": attempt.id,
            "question_id": question_id,
            "is_correct": is_correct,
            "obtained_marks": attempt.obtained_marks
        }
