from app.api.v1.admin_router import router as admin_router
from app.api.v1.auth_router import router as auth_router
from app.api.v1.message_feedback_router import router as message_feedback_router
from app.api.v1.note_router import router as note_router
from app.api.v1.notebook_router import router as notebook_router
from app.api.v1.system_feedback_router import router as system_feedback_router
from app.api.v1.user_router import router as users_router

__all__ = [
    "users_router",
    "auth_router",
    "notebook_router",
    "note_router",
    "message_feedback_router",
    "system_feedback_router",
    "admin_router",
]
