from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.services.enrollment.enrollment_service import EnrollmentService

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.post("/")
async def enroll_student(user_id: int, course_id: int, db: AsyncSession = Depends(get_async_session)):
    service = EnrollmentService(db)

    try:
        result = await service.enroll_student_in_course(user_id, course_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
