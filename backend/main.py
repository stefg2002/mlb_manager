from contextlib import asynccontextmanager

import httpx

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

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

origins = [
    "http://localhost:8000",
    "http://localhost:5173",
]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# TODO: Add routes

"""
Initializes API routes
"""
app.include_router(users.router,prefix="/api/users",tags=["Users"]) 
app.include_router(google.router, prefix="/api/google", tags=["Google"])

#TODO: Add exception handling
@app.exception_handler
async def http_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exc)
    
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/api"):
        return await validation_exception_handler(request, exc)
    
    