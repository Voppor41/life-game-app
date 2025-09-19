import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose.constants import ALGORITHMS
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta

from starlette.status import HTTP_401_UNAUTHORIZED

from database.db import get_db
from database import models

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)) -> models.Player:

    """Получает текущего пользователя по JWT токену"""

    cradentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Brearer"}
    )
    try:
        payload = jwt.decode(token, os.getenv(SECRETE_KEY), algorithms=[ALGORITHMS])
        username: str = payload.get("sub")
        if username is None:
            raise cradentials_exception
    except JWTError:
        raise cradentials_exception

    user = db.query(models.Player).filter(models.Player.username == username).first()
    if user is None:
        raise cradentials_exception
    return user

def get_current_active_user(current_user: models.Player = Depends(get_current_user)) -> models.Player:
    """Проверяет что пользователь активен"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def verify_password(plain_password: str, hashed_password: str) -> str:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, os.getenv(SECRETE_KEY), algorithm=[ALGORITHMS])
    return encode_jwt