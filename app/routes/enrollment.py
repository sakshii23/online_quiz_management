from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import admin_only, get_current_user
from app.database import get_async_session
from app.models import User
from app.schemas import EnrollmentCreate, EnrollmentResponse, EnrollmentUpdate
from app.services.enrollment_service import create_enrollment, edit_enrollment

router = APIRouter()


@router.post("/", response_model=EnrollmentResponse)
async def enroll_course(
    data: EnrollmentCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    return await create_enrollment(current_user.id, data, db)


@router.put("/{enrollment_id}", response_model=EnrollmentResponse)
async def update_enrollment(
    enrollment_id: int = Path(..., description="ID of the enrollment to update"),
    data: EnrollmentUpdate = Depends(),
    db: AsyncSession = Depends(get_async_session),
    admin_only=Depends(admin_only),
):
    return await edit_enrollment(enrollment_id, data, db)
