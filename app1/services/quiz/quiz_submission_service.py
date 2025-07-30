from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from app.models import StudentQuizAttempt, Quiz

from sqlalchemy import select, and_
from datetime import datetime
from app.models import StudentQuizAttempt, Quiz, Module, StudentModuleStatus


class QuizService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def submit_quiz(self, student_id: int, quiz_id: int):
        result = await self.db.execute(
            select(StudentQuizAttempt)
            .where(StudentQuizAttempt.student_id == student_id)
            .where(StudentQuizAttempt.quiz_id == quiz_id)
            .where(StudentQuizAttempt.is_submitted == False)
            .order_by(StudentQuizAttempt.id.desc())
        )
        attempt = result.scalars().first()

        if not attempt:
            raise ValueError("No active quiz attempt found.")

        quiz = await self.db.get(Quiz, quiz_id)
        if not quiz:
            raise ValueError("Quiz not found.")

        is_passed = attempt.total_marks >= quiz.passing_marks

        attempt.is_submitted = True
        attempt.submitted_at = datetime.utcnow()
        attempt.is_passed = is_passed

        # Update module completion if passed
        if is_passed:
            current_module_id = quiz.module_id

            # Mark current module as completed
            result = await self.db.execute(
                select(StudentModuleStatus)
                .where(StudentModuleStatus.user_id == student_id)
                .where(StudentModuleStatus.module_id == current_module_id)
            )
            status = result.scalars().first()
            if status and not status.is_completed:
                status.is_completed = True

            # Unlock next module
            result = await self.db.execute(
                select(Module)
                .where(Module.course_id == quiz.course_id)
                .order_by(Module.order)
            )
            all_modules = result.scalars().all()
            current_idx = next((i for i, m in enumerate(all_modules) if m.id == current_module_id), -1)

            if current_idx != -1 and current_idx + 1 < len(all_modules):
                next_module = all_modules[current_idx + 1]

                # Check if already exists
                result = await self.db.execute(
                    select(StudentModuleStatus)
                    .where(StudentModuleStatus.user_id == student_id)
                    .where(StudentModuleStatus.module_id == next_module.id)
                )
                next_status = result.scalars().first()

                if not next_status:
                    next_status = StudentModuleStatus(
                        user_id=student_id,
                        module_id=next_module.id,
                        is_unlocked=True,
                        unlocked_on=datetime.utcnow(),
                        is_completed=False
                    )
                    self.db.add(next_status)
                elif not next_status.is_unlocked:
                    next_status.is_unlocked = True
                    next_status.unlocked_on = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(attempt)

        return {
            "message": "Quiz submitted successfully.",
            "total_marks_obtained": attempt.total_marks,
            "passing_marks": quiz.passing_marks,
            "status": "passed" if is_passed else "failed"
        }
