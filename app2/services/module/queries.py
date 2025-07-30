# app/queries/module_queries.py

from sqlalchemy import and_
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models import (
    StudentModuleStatus,
    Module,
    StudentQuizAttempt,
    Quiz,
    QuizAnswer,
    Question,
)


def get_module_status(student_id: int, module_id: int):
    return select(StudentModuleStatus).where(
        and_(
            StudentModuleStatus.student_id == student_id,
            StudentModuleStatus.module_id == module_id,
        )
    )


def get_attempt(student_id: int, quiz_id: int):
    return select(StudentQuizAttempt).where(
        and_(
            StudentQuizAttempt.student_id == student_id,
            StudentQuizAttempt.quiz_id == quiz_id,
        )
    )


def get_question_by_id(question_id: int):
    return select(Question).where(Question.id == question_id)


def get_quiz_with_questions(quiz_id: int):
    return (
        select(Quiz)
        .options(selectinload(Quiz.questions))
        .where(Quiz.id == quiz_id)
    )


def get_answer_for_attempt(attempt_id: int, question_id: int):
    return select(QuizAnswer).where(
        and_(
            QuizAnswer.attempt_id == attempt_id,
            QuizAnswer.question_id == question_id,
        )
    )


def get_all_correct_answers(attempt_id: int):
    return select(QuizAnswer).where(
        and_(
            QuizAnswer.attempt_id == attempt_id,
            QuizAnswer.is_correct == True,
        )
    )


def get_module_info(module_id: int, order: int = None, course_id: int = None, title: str = None):
    conditions = []
    if order:
        conditions.append(Module.order == order)
    if course_id:
        conditions.append(Module.course_id == course_id)

    if title:
        conditions.append(Module.title == title)
        conditions.append(Module.id != module_id)
    elif module_id:
        conditions.append(Module.id == module_id)

    if order and course_id and module_id:
        return select(Module).where(
            and_(
                *conditions
            )
        )
    else:
        return select(Module).where(Module.id == module_id)


def get_next_module(course_id: int, current_order: int):
    return (
        select(Module)
        .where(and_(Module.course_id == course_id, Module.order > current_order))
        .order_by(Module.order.asc())
        .limit(1)
    )
