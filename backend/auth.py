# TODO: add simple password authentication ('allow usernames or email authentication')
# TODO: add external authentication services (e.g. Google)
from datetime import UTC, datetime, timedelta

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import select

from pwdlib import PasswordHash

from pydantic import BaseModel

from settings import settings

import jwt
from jwt.exceptions import InvalidTokenError

from db import AsyncSession, get_db

import models

class Token(BaseModel):
    access_token: str
    token_type: str

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")

def verify_password(plain_password: str, hashed_password: str):
    if hashed_password is None: #Google users do not have a hashed password
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return password_hash.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.auth.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.auth.secret_key.get_secret_value(), algorithm=settings.auth.algorithm)
    return encoded_jwt

def authenticate_user(user: models.User, password: str):
    if not user:
        verify_password(password, password_hash.hash("dummypassword")) #Throw off attacker timing
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db)]) -> models.User:
    try:
        payload = jwt.decode(token, settings.auth.secret_key.get_secret_value(), algorithms=[settings.auth.algorithm], options={"require": ["exp", "sub"]})
    except InvalidTokenError:
       raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    data = await db.execute(select(models.User).where(models.User.id == user_id_int))
    user = data.scalars().first()

    if not user:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
        )
    return user

CurrentUser = Annotated[models.User, Depends(get_current_user)]