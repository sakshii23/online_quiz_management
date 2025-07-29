from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, model_validator
from datetime import datetime


class RoleEnum(str, Enum):
    admin = "admin"
    student = "student"


class UserProfileCreate(BaseModel):
    contact_no: Optional[str]
    profile_image: Optional[str]
    dob: Optional[date]
    gender: Optional[str]
    batch: Optional[str]
    designation: Optional[str]


class UserProfileResponse(UserProfileCreate):
    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[RoleEnum] = RoleEnum.student
    profile: Optional[UserProfileCreate]


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleEnum
    created_at: datetime
    profile: Optional[UserProfileResponse]

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


# Course
class CourseCreate(BaseModel):
    title: str
    description: Optional[str]


class CourseUpdate(CourseCreate):
    pass


class CourseResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# # -------------------- Module --------------------
class ModuleCreate(BaseModel):
    course_id: int
    title: str
    content: str
    order: int


class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = None


class ModuleResponse(ModuleCreate):
    id: int
    model_config = {"from_attributes": True}


# ENROLLMENT SCHEMAS
class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int
    batch: Optional[str]


class EnrollmentUpdate(EnrollmentCreate):
    pass


class EnrollmentResponse(EnrollmentCreate):
    id: int
    student_id: int
    enrolled_at: datetime
    model_config = {"from_attributes": True}
    enrolled_at: datetime
    model_config = {"from_attributes": True}


# QUIZ SCHEMAS

class QuizCreate(BaseModel):
    module_id: int
    title: str
    description: Optional[str] = None
    total_marks: int
    passing_marks: Optional[int] = 80


class QuizUpdate(BaseModel):
    title: str
    description: Optional[str]
    total_marks: int
    passing_marks: Optional[int]


class QuizResponse(QuizCreate):
    id: int
    model_config = {"from_attributes": True}


# QUESTION SCHEMAS
class QuestionBase(BaseModel):
    text: str = Field(
        ..., min_length=1, max_length=500, description="The question text"
    )
    marks: int = Field(
        ..., gt=0, le=100, description="Marks allocated for this question"
    )
    options: List[str] = Field(
        ..., min_items=2, description="At least 2 options required"
    )
    correct_answer: str = Field(..., description="The correct answer option")

    @model_validator(mode="after")
    def validate_correct_answer(cls, values):
        if values.correct_answer not in values.options:
            raise ValueError("correct_answer must be one of the provided options")
        return values


class QuestionCreate(QuestionBase):
    quiz_id: int = Field(
        ..., gt=0, description="ID of the quiz this question belongs to"
    )


class QuestionUpdate(BaseModel):  # DON'T inherit from QuestionBase
    text: Optional[str] = Field(None, min_length=1, max_length=500)
    marks: Optional[int] = Field(None, gt=0, le=100)
    options: Optional[List[str]] = Field(None, min_items=2)
    correct_answer: Optional[str] = None

    @model_validator(mode="after")
    def validate_update_fields(cls, values):
        if values.correct_answer is not None and values.options is None:
            raise ValueError("Cannot update correct_answer without providing options")
        if values.correct_answer is not None and values.options is not None:
            if values.correct_answer not in values.options:
                raise ValueError("correct_answer must be one of the provided options")
        return values


class QuestionResponse(QuestionBase):
    id: int
    quiz_id: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "quiz_id": 10,
                "text": "What is the capital of France?",
                "marks": 5,
                "options": ["London", "Paris", "Berlin", "Madrid"],
                "correct_answer": "Paris",
            }
        }



# -------------------- Quiz Answer and Qyiz Attempt Schemas --------------------        
class QuizAnswerCreate(BaseModel):
    question_id: int = Field(..., gt=0)
    selected_option: str

class QuizAttemptCreate(BaseModel):
    quiz_id: int
    answers: List[QuizAnswerCreate]
    
    def __str__(self):
        return self.quiz_id

class QuizAnswerResponse(BaseModel):
    question_id: int
    selected_option: str
    is_correct: bool

    class Config:
        from_attributes = True

class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: int
    user_id: int
    submitted_at: datetime
    total_marks: int
    obtained_marks: int
    is_passed: bool
    pdf_path: Optional[str] = None
    # answers: List[QuizAnswerResponse]

    class Config:
        from_attributes = True
    
    
    
# ======================================Module Status Schemas============================================


class StudentModuleStatusBase(BaseModel):
    
    """Base schema containing common fields"""
    
    student_id: int
    module_id: int
    is_unlocked: bool = False
    is_completed: bool = False    
    
    
class StudentModuleStatusCreate(StudentModuleStatusBase):
    
    """Schema for creating new status records"""
    
    pass  


class StudentModuleStatusUpdate(BaseModel):
    
    """Schema for updating status records (all fields optional)"""
    
    is_unlocked: Optional[bool] = None
    is_completed: Optional[bool] = None
    
    class Config:
        extra = "forbid"  # Prevent extra fields
        
class StudentModuleStatusResponse(StudentModuleStatusBase):
    
    """Full output schema including system-generated fields"""
    
    id: int
    unlocked_on: datetime
    
    class Config:
        from_attributes = True  # Enable ORM mode
        json_schema_extra = {
            "example": {
                "id": 1,
                "student_id": 123,
                "module_id": 456,
                "is_unlocked": True,
                "is_completed": False,
                "unlocked_on": "2023-07-20T14:30:00Z"
            }
        }

class QuizAttemptWithModuleStatusResponse(BaseModel):
    attempt: QuizAttemptResponse
    module_status: dict  # or create a proper model for this      
        
# class AdminModuleUnlockRequest(BaseModel):
#     """Special schema for admin unlock requests"""
#     student_id: int
#     module_id: int
#     force_unlock: bool = True
#     force_complete: Optional[bool] = None
    
    
    
# code refactoring and code ko aarange krna and proper documentaion likhna hai
