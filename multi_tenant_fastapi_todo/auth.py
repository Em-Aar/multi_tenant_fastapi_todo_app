from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, status
from multi_tenant_fastapi_todo.db import get_session, User
from typing import Annotated
from sqlmodel import Session, select
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel


SECRET_KEY = 'c0fd47e24bc30a0f6c15a08e09e5bebb8163de53da439971e56cd9371595b0b8'
ALGORITHM = 'HS256'
ACCESS_TOKE_EXPIRE_MINUTE = 30


class Token (BaseModel):
    access_token: str
    token_type: str


class TokenData (BaseModel):
    email: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

'''
tokenUrl declares that the URL '/token' will be the one that the client should use to get the token. 
That information is used in OpenAPI, 
and then in the interactive API documentation systems.

(tokenUrl): FastAPI is using the same name as in the OpenAPI spec.

oauth2_scheme is an instance of OAuth2PasswordBearer, 
and also callable. 
We can pass it in a dependency with 'Depends()' 

'''

pwd_cntxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

# function to generate hashpassword


def hash_password(password):
    return pwd_cntxt.hash(password)

# function to verify password


def verify_password(plain_password, hashed_password):
    return pwd_cntxt.verify(plain_password, hashed_password)

# function to get user from db


def get_user_from_db(email: str, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    return user

# function to authenticate user


def authenticate_user(email: str, password: str, session: Session = Depends(get_session)):
    user_from_db = get_user_from_db(email, session)
    if not user_from_db:
        return False
    if not verify_password(password, user_from_db.password):
        return False
    return user_from_db


# create token for the user
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    'exp' (expiration time): 
    It's a standard claim (field) within the payload of a JSON Web Token (JWT), and it represents the expiration time of the token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    ecoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return ecoded_jwt

# verify access token


def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Session = Depends(get_session)
):
    """
    'sub' (subject):
    In the context of JWT (JSON Web Token) decoding, "sub" stands for subject. It's a standard claim (field) within the JWT payload that identifies the principal subject of the toke

    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials, Please login again",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user_from_db(email=token_data.email, session=session)
    if user is None:
        raise credentials_exception
    return user
