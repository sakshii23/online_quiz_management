from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import admin_only
from app.database import get_async_session
from app.schemas import ModuleCreate, ModuleResponse, ModuleUpdate
from app.services.module_service import CreateModule, update_module

router = APIRouter()


@router.post("/", response_model=ModuleResponse)
async def create_module(
    data: ModuleCreate,
    db: AsyncSession = Depends(get_async_session),
    admin=Depends(admin_only),
):
    return await CreateModule(data, db)

@router.put("/{module_id}", response_model=ModuleResponse)
async def edit_module(
    module_id: int = Path(..., description="ID of the module to update"),
    data: ModuleUpdate = Depends(),
    db: AsyncSession = Depends(get_async_session),
    _=Depends(admin_only),
):
    return await update_module(module_id, data, db)
