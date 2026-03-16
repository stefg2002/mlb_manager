from contextlib import asynccontextmanager

import httpx

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError

from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from routers import users, google
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
app.add_middleware(SessionMiddleware, https_only=False, same_site="lax",secret_key=settings.auth.secret_key.get_secret_value())

# TODO: Add routes

"""
Initializes API routes
"""
app.include_router(users.router,prefix="/api/users",tags=["Users"]) 
app.include_router(google.router, prefix="/google", tags=["Google"])

#TODO: Add exception handling
@app.exception_handler
async def http_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exc)
    
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/api"):
        return await validation_exception_handler(request, exc)
    
    