from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Enrollment
from app.schemas import EnrollmentCreate, EnrollmentUpdate
# from app.services.module_service import unlock_first_module


async def create_enrollment(user_id: int, data: EnrollmentCreate, db: AsyncSession):
    enrollment = Enrollment(student_id=user_id, **data.dict())
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    # await unlock_first_module(user_id, data.course_id, db)
    return enrollment


async def edit_enrollment(enrollment_id: int, data: EnrollmentUpdate, db: AsyncSession):

    result = await db.execute(select(Enrollment).filter(Enrollment.id == enrollment_id))
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
