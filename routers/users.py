# TODO: Add API endpoints for Users
# TODO: Add authorization to specified endpoints
from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from sqlalchemy import select

from fastapi import APIRouter, HTTPException, status, Request, Depends

from typing import Annotated

from settings import settings
from db import AsyncSession, get_db

from auth import Token, authenticate_user, create_access_token, CurrentUser, get_password_hash

import models

UsernameMeta = Annotated[str, Field(min=1, max=50)]
EmailMeta = Annotated[EmailStr, Field(min=1, max=100)]

class User(BaseModel):
    username: UsernameMeta
    email: EmailMeta

class UserPost(User):
    password: Annotated[str, Field(min=8)]

class UserGetPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: UsernameMeta
    id: int

class UserGetPrivate(UserGetPublic):
    email: EmailMeta

class UserUpdate(BaseModel):
    username: UsernameMeta | None = None
    email: EmailMeta | None = None

router = APIRouter()

"""
URL=/api/users/
"""

@router.post("", response_model=UserGetPublic)
async def create_user(user: UserPost, db: Annotated[AsyncSession, Depends(get_db)]):
    # TODO: check if username and email exist
    data = await db.execute(select(models.User).where(models.User.username == user.username))
    existing_user = data.scalars().first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    
    data = await db.execute(select(models.User).where(models.User.email == user.email))
    existing_email = data.scalars().first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")

    db_user = models.User(username=user.username, email=user.email, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user

@router.post("/token")
async def login(db: Annotated[AsyncSession, Depends(get_db)], form_data: Annotated[OAuth2PasswordRequestForm,Depends()]):
    data = await db.execute(select(models.User).where(models.User.username == form_data.username))
    db_user = data.scalars().first()
    user = authenticate_user(db_user, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Incorrect username or password", 
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token_expires = timedelta(minutes=settings.auth.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")

@router.get("/google")
async def get_google_user(request: Request):
    user_session = request.session.get("user")
    if not user_session:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")
    return {
        "session_data": user_session
    }

@router.get("/me", response_model=UserGetPrivate)
async def get_cur_user(request: Request, current_user: CurrentUser):
    return current_user

@router.get("/{user_id}", response_model=UserGetPublic)
async def get_user(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    pass

@router.patch("/{user_id}", response_model=UserGetPrivate)
async def update_user(user_id: int, current_user: CurrentUser, user_update: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access to user account")
    
    data = await db.execute(select(models.User).where(models.User.id == user_id))
    user = data.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user_update.username is not None and user_update.username != user.username:
        result = await db.execute(select(models.User).where(models.User.username == user_update.username))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    if user_update.email is not None and user_update.email != user.email:
        result = await db.execute(select(models.User).where(models.User.email == user_update.email))
        existing_email = result.scalars().first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already in use")

    update = user_update.model_dump(exclude_unset=True)
    for field, value in update.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user():
    #TODO: check for authorization
    #TODO: remove user from database
    pass