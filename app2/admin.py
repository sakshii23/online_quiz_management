from sqladmin import Admin, ModelView
from app.database import engine
from app.models import User
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request


#This page will implement the authentication for your admin pannel
class AdminAuth(AuthenticationBackend):

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username= form.get("email")
        password= form.get("password")
        session = session()
        user = session.query(User).filter(User.username == username).first()
        if user and password== user.password:
            if user.is_admin:
                request.session.update({"token": beta_user.username})
                return True
        else:
            False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        return token is not None


# create a view for your models
class UsersAdmin(ModelView, model=User):
    column_list = [
        'id', 'email', 'first_name', 'last_name', 'is_admin'
    ]


# add the views to admin
def create_admin(app):
    authentication_backend = AdminAuth(secret_key="supersecretkey")
    admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)
    admin.add_view(UsersAdmin)
    
    return admin