from sqlalchemy import and_
from sqlalchemy.future import select

from app.models import Enrollment, Course, Module, StudentModuleStatus


def get_enrollment(student_id: int = None, course_id: int = None, enrollment_id: int = None):
    if student_id and course_id:
        return select(Enrollment).where(
            and_(Enrollment.student_id == student_id, Enrollment.course_id == course_id)
        )
    elif enrollment_id:
        return select(Enrollment).filter(Enrollment.id == enrollment_id)
    return None


def get_course_modules(course_id: int):
    return (
        select(Module).where(Module.course_id == course_id).order_by(Module.order)
    )


def get_next_module(course_id: int, current_order: int):
    return (
        select(Module)
        .where(and_(Module.course_id == course_id, Module.order > current_order))
        .order_by(Module.order.asc())
        .limit(1)
    )


def get_module_status(student_id: int, module_id: int):
    return select(StudentModuleStatus).where(
        and_(
            StudentModuleStatus.student_id == student_id,
            StudentModuleStatus.module_id == module_id
        )
    )
