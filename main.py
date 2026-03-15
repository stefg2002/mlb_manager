from contextlib import asynccontextmanager

import httpx

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError

from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from routers import users
from google_auth import oauth

from db import engine

import models
from settings import settings

"""
Startup and shutdown sequence for database engine
"""
@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.auth.secret_key.get_secret_value())

# TODO: Add routes

"""
Initializes API routes
"""
app.include_router(users.router,prefix="/api/users",tags=["Users"])

@app.get("/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for('auth_callback')
    print(f"GOOGLE | {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/google/auth")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token['userinfo']
    return user

@app.post("/google/revoke", status_code=status.HTTP_204_NO_CONTENT)
async def revoke(token: str):
    async with httpx.AsyncClient() as client:
        response=await client.post(
            f"https://oauth2.googleapis.com/revoke?token={token}"
        )
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to revoke token") 

#TODO: Add exception handling
@app.exception_handler
async def http_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exc)
    
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/api"):
        return await validation_exception_handler(request, exc)
    
    