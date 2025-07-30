from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.schemas import ModuleUpdate, ModuleResponse
from app.services.module.module_service import ModuleService

router = APIRouter(prefix="/modules", tags=["Modules"])


@router.put("/{module_id}", response_model=ModuleResponse)
async def update_module_api(
        module_id: int,
        data: ModuleUpdate,
        db: AsyncSession = Depends(get_async_session)
):
    return await ModuleService.update_module(module_id, data, db)
