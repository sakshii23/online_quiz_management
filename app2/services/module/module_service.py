from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from app.models import Module
from app.schemas import ModuleUpdate
from app.services.module.queries import (
    get_module_info
)


class ModuleService:

    @staticmethod
    async def update_module(module_id: int, data: ModuleUpdate, db: AsyncSession):
        # Fetch the module
        result = await db.execute(get_module_info(module_id=module_id))
        module = result.scalars().first()

        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )

        # Check for duplicate order within the course
        if data.order is not None and data.order != module.order:
            duplicate_order = await db.execute(
                get_module_info(
                    course_id=module.course_id,
                    order=data.order,
                    module_id=module_id
                )
            )
            if duplicate_order.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Module with order {data.order} already exists in this course"
                )

        # Check for duplicate title within the course
        if data.title is not None and data.title != module.title:
            duplicate_title = await db.execute(
                get_module_info(
                    course_id=module.course_id,
                    title=data.title,
                    module_id=module_id
                )
            )
            if duplicate_title.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Module with title '{data.title}' already exists in this course"
                )

        # Update allowed fields
        if data.title is not None:
            module.title = data.title
        if data.content is not None:
            module.content = data.content
        if data.order is not None:
            module.order = data.order

        await db.commit()
        await db.refresh(module)

        return module
