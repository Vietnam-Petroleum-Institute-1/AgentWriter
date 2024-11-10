from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import (
    admin_router,
    auth_router,
    message_feedback_router,
    note_router,
    notebook_router,
    system_feedback_router,
    users_router,
    chat_router
)
from app.core.config import settings
from app.core.exception_handler import (
    http_exception_handler,
    validation_exception_handler,
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(notebook_router)
api_router.include_router(note_router)
# api_router.include_router(message_feedback_router)
api_router.include_router(system_feedback_router)
api_router.include_router(admin_router)
api_router.include_router(chat_router)
app.include_router(api_router)
