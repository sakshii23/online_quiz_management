from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from sqlalchemy import inspect, text

from app.database import engine
from app.models import Base, User
from app.routes import auth, course, enrollment, module, question, quiz, quiz_answer
from app.admin import create_admin


async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)

        # Check if column exists using sync inspection
        def check_and_add_column(conn):
            inspector = inspect(conn)
            columns = inspector.get_columns("quizzes")
            column_names = [column["name"] for column in columns]

            if "total_marks" not in column_names:
                conn.execute(
                    text(
                        "ALTER TABLE quizzes ADD COLUMN total_marks INTEGER DEFAULT 800"
                    )
                )

        await conn.run_sync(check_and_add_column)
    yield


# Create app with lifespan
app = FastAPI(title="Student Learning App")

from sqladmin import Admin, ModelView


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email]


app = FastAPI()
admin = Admin(app, engine)  # Your SQLAlchemy engine
admin.add_view(UserAdmin)


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Student Learning App",
        version="1.0.0",
        description="API with JWT Auth (Bearer)",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

#  Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(course.router, prefix="/courses", tags=["courses"])
app.include_router(enrollment.router, prefix="/enrollment", tags=["enrollment"])
app.include_router(module.router, prefix="/modules", tags=["modules"])
app.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
app.include_router(question.router, prefix="/questions", tags=["questions"])
app.include_router(quiz_answer.router, prefix="/quiz-attempts", tags=["Quiz Attempts"])
