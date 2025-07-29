import enum

from sqlalchemy import JSON, Boolean, Column, Date, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

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

    profile = relationship(
        "UserProfile", uselist=False, back_populates="user", cascade="all, delete"
    )

    module_statuses = relationship(  # Keep this name consistent
        "StudentModuleStatus", 
        back_populates="user",  # Changed from 'student' to 'user'
        cascade="all, delete-orphan"
    )



class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    contact_no = Column(String(20), nullable=True)
    profile_image = Column(String, nullable=True)
    dob = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    batch = Column(String(20), nullable=True)
    designation = Column(String(50), nullable=True)

    user = relationship("User", back_populates="profile")


# -------------------- Course --------------------


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(String(150), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modules = relationship(
        "Module", 
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Module.order"  # Ensures modules are ordered correctly
    )


#     modules = relationship("Module", back_populates="course")
#     enrollments = relationship("Enrollment", back_populates="course")

# # -------------------- Enrollment --------------------


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"))
    batch = Column(String, nullable=True)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())


#     student = relationship("User", back_populates="enrollments")
#     course = relationship("Course", back_populates="enrollments")


# # -------------------- Module --------------------
class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"))
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)
    order = Column(Integer, nullable=False)  # Determines module sequence
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    quizzes = relationship("Quiz", back_populates="module")
    course = relationship("Course", back_populates="modules")
    quiz = relationship("Quiz", uselist=False, back_populates="module")  # One quiz per module
    student_statuses = relationship(
        "StudentModuleStatus",
        back_populates="module",
        cascade="all, delete-orphan"
    )


# course = relationship("Course", back_populates="modules")
# quiz = relationship("Quiz", uselist=False, back_populates="module")

# # -------------------- Quiz --------------------
class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"))
    title = Column(String(100))
    description = Column(Text)
    passing_marks = Column(Integer, default=800)  # Keep absolute marks
    total_marks = Column(Integer, default=800)   # Keep total marks
    is_survey = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    module = relationship("Module", back_populates="quizzes")
















# class Quiz(Base):
#     __tablename__ = "quizzes"

#     id = Column(Integer, primary_key=True, index=True)
#     module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"))
#     title = Column(String(100))
#     description = Column(Text)
#     passing_marks = Column(Integer, default=800)
#     total_marks = Column(Integer, default=800)
#     is_survey = Column(Boolean, default=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

    # module = relationship("Module", back_populates="quiz")
    # questions = relationship("Question", back_populates="quiz", cascade="all, delete")
    # attempts = relationship("StudentQuizAttempt", back_populates="quiz")


# # -------------------- Question --------------------


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"))
    text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # {"a": "Answer A", "b": "Answer B"}
    correct_answer = Column(String, nullable=False)
    marks = Column(Integer, default=100)


#     quiz = relationship("Quiz", back_populates="questions")



 # -------------------- Quiz Attempt --------------------

class StudentQuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"))
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    total_marks = Column(Integer)
    obtained_marks = Column(Integer)
    is_passed = Column(Boolean, default=False)
    pdf_path = Column(String, nullable=True)

    # user = relationship("User", back_populates="quiz_attempts")
    # quiz = relationship("Quiz", back_populates="attempts")
    # answers = relationship("QuizAnswer", back_populates="attempt", cascade="all, delete")

# -------------------- Quiz Answer by student --------------------

class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id", ondelete="CASCADE"))
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
    selected_option = Column(String)
    is_correct = Column(Boolean, default=False)


class StudentModuleStatus(Base):
    __tablename__ = "student_module_status"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"))
    is_unlocked = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    unlocked_on = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="module_statuses")
    module = relationship("Module", back_populates="student_statuses")