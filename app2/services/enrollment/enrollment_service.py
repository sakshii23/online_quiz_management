from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Enrollment, Module, StudentModuleStatus
from app.schemas import EnrollmentCreate, EnrollmentUpdate
from app.services.enrollment.queries import (
    get_enrollment,
    get_course_modules,
    get_next_module,
    get_module_status,
)


# from app.services.module_service import unlock_first_module


async def create_enrollment(user_id: int, data: EnrollmentCreate, db: AsyncSession):
    enrollment = Enrollment(student_id=user_id, **data.dict())
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    # await unlock_first_module(user_id, data.course_id, db)
    return enrollment


async def edit_enrollment(enrollment_id: int, data: EnrollmentUpdate, db: AsyncSession):
    result = await db.execute(get_enrollment(enrollment_id=enrollment_id))
    enrollment = result.scalars().first()

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    # Update fields if provided
    if data.student_id is not None:
        enrollment.student_id = data.student_id
    if data.course_id is not None:
        enrollment.course_id = data.course_id
    if data.batch is not None:
        enrollment.batch = data.batch

    await db.commit()
    await db.refresh(enrollment)
    return enrollment


class EnrollmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def enroll_student_in_course(self, user_id: int, course_id: int):
        # Step 1: Create enrollment entry
        enrollment = Enrollment(student_id=user_id, course_id=course_id)
        self.db.add(enrollment)

        # Step 2: Fetch all modules in course ordered by order
        modules = await self.db.execute(
            get_course_modules(course_id=course_id)
        )
        modules = modules.scalars().all()

        if not modules:
            raise ValueError("No modules found in this course.")

        # Step 3: Initialize StudentModuleStatus for all modules
        first_module_id = modules[0].id

        for module in modules:
            status = StudentModuleStatus(
                student_id=user_id,
                module_id=module.id,
                is_unlocked=(module.id == first_module_id),  # unlock only first
                best_score=None,
                last_attempt_id=None,
                is_completed=False,
                unlocked_on=datetime.utcnow() if module.id == first_module_id else None
            )
            self.db.add(status)

        await self.db.commit()
        return {"message": "Enrollment successful"}
