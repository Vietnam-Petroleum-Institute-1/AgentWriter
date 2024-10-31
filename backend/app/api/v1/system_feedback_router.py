from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.system_feedback import SystemFeedback
from app.models.user import User
from app.schemas.system_feedback import (
    SystemFeedbackCreate,
    SystemFeedbackResponse,
    SystemFeedbackUpdate,
)
from app.services.system_feedback import SystemFeedbackService

router = APIRouter(prefix="/system_feedbacks", tags=["System Feedbacks"])


@router.post("/", response_model=SystemFeedbackResponse)
async def create_system_feedback(
    system_feedback_in: SystemFeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    system_feedback_service = SystemFeedbackService(db)
    system_feedback = await system_feedback_service.create_system_feedback(
        system_feedback_in, current_user.user_id
    )
    return system_feedback


@router.get("/", response_model=List[SystemFeedbackResponse])
async def read_system_feedbacks(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    system_feedback_service = SystemFeedbackService(db)
    system_feedbacks = await system_feedback_service.get_system_feedbacks(
        skip=skip, limit=limit
    )
    return system_feedbacks


@router.get("/{feedback_id}", response_model=SystemFeedbackResponse)
async def read_system_feedback(feedback_id: str, db: AsyncSession = Depends(get_db)):
    system_feedback_service = SystemFeedbackService(db)
    system_feedback = await system_feedback_service.get_system_feedback(feedback_id)
    if not system_feedback:
        raise HTTPException(status_code=404, detail="System feedback not found")
    return system_feedback


@router.put("/{feedback_id}", response_model=SystemFeedbackResponse)
async def update_system_feedback(
    feedback_id: str,
    system_feedback_in: SystemFeedbackUpdate,
    db: AsyncSession = Depends(get_db),
):
    system_feedback_service = SystemFeedbackService(db)
    system_feedback = await system_feedback_service.update_system_feedback(
        feedback_id, system_feedback_in
    )
    if not system_feedback:
        raise HTTPException(status_code=404, detail="System feedback not found")
    return system_feedback


@router.delete("/{feedback_id}", response_model=SystemFeedbackResponse)
async def delete_system_feedback(feedback_id: str, db: AsyncSession = Depends(get_db)):
    system_feedback_service = SystemFeedbackService(db)
    system_feedback = await system_feedback_service.delete_system_feedback(feedback_id)
    if not system_feedback:
        raise HTTPException(status_code=404, detail="System feedback not found")
    return system_feedback
