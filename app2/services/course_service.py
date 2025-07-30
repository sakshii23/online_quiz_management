from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Course
from app.schemas import CourseCreate, CourseUpdate


async def create_course(course: CourseCreate, db: AsyncSession):
    """Create a new course (admin only)"""
    # Check if course with same code already exists
    result = await db.execute(select(Course).filter(Course.title == course.title))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course with this code already exists",
        )

    new_course = Course(**course.dict())
    db.add(new_course)
    await db.commit()
    await db.refresh(new_course)
    return new_course


async def update_course(course_id: int, data: CourseUpdate, db: AsyncSession):
    """Update course details (admin only)"""
    result = await db.execute(select(Course).filter(Course.id == course_id))
    course = result.scalars().first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Prevent duplicate course codes
    if data.title and data.title != course.title:
        result = await db.execute(select(Course).filter(Course.title == data.title))
        if result.scalars().first():
            raise HTTPException(
                status_code=400, detail="Another course with this code already exists"
            )

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(course, key):  # Optional safety check
                setattr(course, key, value)

    await db.commit()
    await db.refresh(course)
    return course
