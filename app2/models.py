from sqlalchemy import JSON, Boolean, Column, Date, DateTime, Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class RoleEnum(str, enum.Enum):
    admin = "admin"
    student = "student"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(SqlEnum(RoleEnum), default=RoleEnum.student, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("UserProfile", uselist=False, back_populates="user", cascade="all, delete")
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    module_statuses = relationship("StudentModuleStatus", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("StudentQuizAttempt", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    contact_no = Column(String(20))
    profile_image = Column(String)
    dob = Column(Date)
    gender = Column(String(10))
    batch = Column(String(20))
    designation = Column(String(50))

    user = relationship("User", back_populates="profile")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(String(150), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan", order_by="Module.order")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"))
    batch = Column(String)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"))
    title = Column(String(100), nullable=False)
    content = Column(Text)
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 🔑 prerequisite for custom unlocking logic
    prerequisite_module_id = Column(Integer, ForeignKey("modules.id"), nullable=True)
    prerequisite_module = relationship("Module", remote_side=[id], backref="unlocked_by")

    course = relationship("Course", back_populates="modules")
    quiz = relationship("Quiz", back_populates="module", uselist=False)
    student_statuses = relationship("StudentModuleStatus", back_populates="module", cascade="all, delete-orphan")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"))
    title = Column(String(100))
    description = Column(Text)
    passing_marks = Column(Integer, default=800)
    total_marks = Column(Integer, default=800)
    is_survey = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    module = relationship("Module", back_populates="quiz")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("StudentQuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"))
    text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # e.g. {"a": "Answer A", "b": "Answer B"}
    correct_answer = Column(String, nullable=False)
    marks = Column(Integer, default=100)

    quiz = relationship("Quiz", back_populates="questions")


class StudentQuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"))
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    total_marks = Column(Integer)
    obtained_marks = Column(Integer)
    is_passed = Column(Boolean, default=False)
    pdf_path = Column(String)

    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")
    answers = relationship("QuizAnswer", back_populates="attempt", cascade="all, delete-orphan")


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id", ondelete="CASCADE"))
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
    selected_option = Column(String)
    is_correct = Column(Boolean, default=False)

    attempt = relationship("StudentQuizAttempt", back_populates="answers")


class StudentModuleStatus(Base):
    __tablename__ = "student_module_status"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"))
    is_unlocked = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    best_score = Column(Integer, nullable=True)
    last_attempt_id = Column(Integer, ForeignKey("quiz_attempts.id", ondelete="SET NULL"), nullable=True)
    unlocked_on = Column(DateTime(timezone=True), default=None)

    user = relationship("User", back_populates="module_statuses")
    module = relationship("Module", back_populates="student_statuses")
    last_attempt = relationship("StudentQuizAttempt", foreign_keys=[last_attempt_id])


class StudentCourseProgress(Base):
    __tablename__ = "student_course_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"))
    current_module_id = Column(Integer, ForeignKey("modules.id", ondelete="SET NULL"), nullable=True)
    total_modules = Column(Integer, nullable=True)
    completed_modules = Column(Integer, default=0)
    percentage_completed = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    student = relationship("User")
    course = relationship("Course")
    current_module = relationship("Module")
