from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import admin_only
from app.database import get_async_session
from app.schemas import CourseCreate, CourseResponse, CourseUpdate
from app.services.course_service import create_course, update_course

router = APIRouter()


@router.post("/", response_model=CourseResponse)
async def add_course(
    course: CourseCreate,
    db: AsyncSession = Depends(get_async_session),
    admin=Depends(admin_only),
):
    return await create_course(course, db)


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course_route(
    course_id: int,
    data: CourseUpdate,
    db: AsyncSession = Depends(get_async_session),
    admin=Depends(admin_only),
):
    return await update_course(course_id, data, db)
