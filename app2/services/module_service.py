from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from app.models import Module, Quiz, StudentModuleStatus
from app.schemas import ModuleCreate, ModuleUpdate


async def CreateModule(module: ModuleCreate, db: AsyncSession):
    """Create a new module with validation for uniqueness within course"""

    # Check if module with same order already exists in this course
    existing_module = await db.execute(
        select(Module)
        .where(
            and_(
                Module.course_id == module.course_id,
                Module.order == module.order
            )
        )
    )

    if existing_module.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Module with order {module.order} already exists in this course"
        )

    # Check if module title is unique within course
    existing_title = await db.execute(
        select(Module)
        .where(
            and_(
                Module.course_id == module.course_id,
                Module.title == module.title
            )
        )
    )

    if existing_title.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Module with title '{module.title}' already exists in this course"
        )

    new_module = Module(**module.dict())
    db.add(new_module)
    await db.commit()
    await db.refresh(new_module)
    return new_module


async def update_module(module_id: int, data: ModuleUpdate, db: AsyncSession):
    """Update module with validation for uniqueness within course"""

    result = await db.execute(select(Module).filter(Module.id == module_id))
    module = result.scalars().first()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )

    # Validate order uniqueness if being updated
    if data.order is not None and data.order != module.order:
        existing_order = await db.execute(
            select(Module)
            .where(
                and_(
                    Module.course_id == module.course_id,
                    Module.order == data.order,
                    Module.id != module_id
                )
            )
        )
        if existing_order.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Module with order {data.order} already exists in this course"
            )

    # Validate title uniqueness if being updated
    if data.title is not None and data.title != module.title:
        existing_title = await db.execute(
            select(Module)
            .where(
                and_(
                    Module.course_id == module.course_id,
                    Module.title == data.title,
                    Module.id != module_id
                )
            )
        )
        if existing_title.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Module with title '{data.title}' already exists in this course"
            )

    # Update fields
    if data.title is not None:
        module.title = data.title
    if data.content is not None:
        module.content = data.content
    if data.order is not None:
        module.order = data.order

    await db.commit()
    await db.refresh(module)
    return module


# handle_module_unlocking


# app/services/module_service.py


async def unlock_first_module(student_id: int, course_id: int, db: AsyncSession):
    """Unlocks Module 1 when student enrolls in a course"""
    first_module = await db.scalar(
        select(Module)
        .where(Module.course_id == course_id)
        .order_by(Module.order)
        .limit(1)
    )

    if first_module:
        db.add(StudentModuleStatus(
            student_id=student_id,
            module_id=first_module.id,
            is_unlocked=True,
            is_completed=False
        ))
        await db.commit()

# async def CreateModule(module: ModuleCreate, db: AsyncSession):
#     """Create a new module (admin only)"""

#     # Check if module with same name already exists
#     result = await db.execute(select(Module).filter(Module.order == module.order))
#     if result.scalars().first():
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="module with this code already exists",
#         )

#     new_module = Module(**module.dict())
#     db.add(new_module)
#     await db.commit()
#     await db.refresh(new_module)
#     return new_module


# async def update_module(module_id: int, data: ModuleUpdate, db: AsyncSession):

#     result = await db.execute(select(Module).filter(Module.id == module_id))
#     module = result.scalars().first()

#     if not module:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
#         )

#     # Update fields if provided
#     if data.title is not None:
#         module.title = data.title
#     if data.content is not None:
#         module.content = data.content
#     if data.order is not None:
#         module.order = data.order

#     await db.commit()
#     await db.refresh(module)
#     return module
