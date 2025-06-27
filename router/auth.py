from datetime import datetime, timezone, timedelta
from typing import Annotated

from fastapi import HTTPException, Path, APIRouter
from fastapi.params import Depends
from pydantic import BaseModel, Field
from starlette import status
from database import db_dependency
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

SECRET_KEY = '09df8bfbc448c7d74c0ab130bbf8e9e94fe893b9a6da778a4e834d15530a7ca'
ALGORITHM = 'HS256'

authRouter = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

class UserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=3, max_length=100)
    first_name: str = Field(min_length=3, max_length=100)
    last_name: str = Field(min_length=3, max_length=100)
    role: str = Field(min_length=3, max_length=100)
    is_active: bool = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oath_barer = OAuth2PasswordBearer(tokenUrl="/auth/token")

@authRouter.get("/", status_code= status.HTTP_200_OK)
def get_auth():
    return {"auth": "ok"}

@authRouter.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(userRequest: UserRequest, db: db_dependency):
    # user_model = Users(**userRequest.model_dump())
    # user_model.hashed_password = userRequest.password

    user_model = Users(
        username=userRequest.username,
        email=userRequest.email,
        hashed_password=bcrypt_context.hash(userRequest.password),
        first_name=userRequest.first_name,
        last_name=userRequest.last_name,
        role=userRequest.role,
        is_active=userRequest.is_active,
    )

    db.add(user_model)
    db.commit()

@authRouter.post("/token", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                           db: db_dependency):

    user = authenticate_user(
        form_data.username,
        form_data.password,
        db
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))

    return {
        "access_token": token,
        "token_type": "bearer",
    }


# @authRouter.get("/current-user", status_code=status.HTTP_200_OK)
async def get_current_user(token: Annotated[str, Depends(oath_barer)]):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username: str = payload.get("username")
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")

        if not username or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return {"username": username, "user_id": user_id, "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        return False

    if not bcrypt_context.verify(password, user.hashed_password):
        return False

    return user


def create_access_token(username: str, user_id: str, role: str, expire: timedelta):
    encode = {'username': username, 'user_id': user_id, 'role': role}
    expire = datetime.now(timezone.utc) + expire
    encode.update({'exp': expire})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)