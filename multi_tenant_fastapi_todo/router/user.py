from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from dailydo_todo_app import db
from dailydo_todo_app.auth import get_current_user, get_user_from_db, hash_password
from dailydo_todo_app.db import get_session
from dailydo_todo_app.db import User
from typing import Annotated
from sqlmodel import Session, select
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

# route for user root
@router.get("/")
def user_root():
    return {"message": "Welcome to dailyDo todo app user page. Please register or login to continue"}


# route for user registration
@router.post('/register')
async def create_user(
    new_user: Annotated[OAuth2PasswordRequestForm, Depends()], 
    session: Annotated[Session, Depends(get_session)]
    ): # Depends() without parameter indicates that the argument itself is a dependency that FastAPI knows how to handle.

    db_user = get_user_from_db(new_user.username, session)
    print(db_user)
    if db_user:
        raise HTTPException(status_code=409, detail=f""" "Whoops! {new_user.username} is already taken. Did you mean to sign in?""")
    user = User(email = new_user.username, password = hash_password(new_user.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": f"{user.email} successfully registered"}


@router.get('/me', response_model= User)
async def me(current_user: Annotated[User, Depends(get_current_user)]):
        print(f""" from me route {current_user}""")
        return current_user