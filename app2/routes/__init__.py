# routes/__init__.py

from fastapi import APIRouter
from app.services.module.api import router as module_router
from app.services.quiz.api import router as quiz_router
from app.services.enrollment.api import router as enrollment_router

router = APIRouter()

router.include_router(module_router)
router.include_router(quiz_router)
router.include_router(enrollment_router)
