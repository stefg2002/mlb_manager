from datetime import timedelta
from typing import Annotated

from sqlalchemy import select

from fastapi import APIRouter, Depends, Request, status, HTTPException

from google_auth import oauth

from routers import users

from settings import settings

from auth import create_access_token

import models

from db import AsyncSession, get_db

router = APIRouter()

@router.get("/login", include_in_schema=True)
async def google_login(request: Request):
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth", include_in_schema=False)
async def auth_callback(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    token = await oauth.google.authorize_access_token(request)
    google_user = token['userinfo']

    g_id = google_user['sub']

    data = await db.execute(select(models.User).where(models.User.google_id == g_id))
    user = data.scalars().first()

    if not user: # Google account does not exist in database
        db_user = models.User(username=f"{google_user['given_name']}{google_user['family_name']}", email=google_user['email'], google_id=g_id, type="google")
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        access_token_expires=timedelta(minutes=settings.auth.access_token_expire_minutes)
        access_token = create_access_token(data={"sub": str(db_user.id)}, expires_delta=access_token_expires)
    else:
        access_token_expires=timedelta(minutes=settings.auth.access_token_expire_minutes)
        access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)

    # request.session["user"] = {"id": google_user['sub'], "email": google_user['email']}
    return users.Token(access_token=access_token, token_type="bearer")

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(token: str, request: Request):
    request.session.clear()
    