from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.message_feedback import MessageFeedback
from app.models.user import User
from app.schemas.message_feedback import (
    MessageFeedbackCreate,
    MessageFeedbackResponse,
    MessageFeedbackUpdate,
)
from app.services.message_feedback import MessageFeedbackService

router = APIRouter(prefix="/message_feedbacks", tags=["Message Feedbacks"])


@router.post("/", response_model=MessageFeedbackResponse)
async def create_message_feedback(
    message_feedback_in: MessageFeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    message_feedback_service = MessageFeedbackService(db)
    message_feedback = await message_feedback_service.create_message_feedback(
        message_feedback_in, current_user.user_id
    )
    return message_feedback


@router.get("/", response_model=List[MessageFeedbackResponse])
async def read_message_feedbacks(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    message_feedback_service = MessageFeedbackService(db)
    message_feedbacks = await message_feedback_service.get_message_feedbacks(
        skip=skip, limit=limit
    )
    return message_feedbacks


@router.get("/{feedback_id}", response_model=MessageFeedbackResponse)
async def read_message_feedback(feedback_id: str, db: AsyncSession = Depends(get_db)):
    message_feedback_service = MessageFeedbackService(db)
    message_feedback = await message_feedback_service.get_message_feedback(feedback_id)
    if not message_feedback:
        raise HTTPException(status_code=404, detail="Message feedback not found")
    return message_feedback


@router.put("/{feedback_id}", response_model=MessageFeedbackResponse)
async def update_message_feedback(
    feedback_id: str,
    message_feedback_in: MessageFeedbackUpdate,
    db: AsyncSession = Depends(get_db),
):
    message_feedback_service = MessageFeedbackService(db)
    message_feedback = await message_feedback_service.update_message_feedback(
        feedback_id, message_feedback_in
    )
    if not message_feedback:
        raise HTTPException(status_code=404, detail="Message feedback not found")
    return message_feedback


@router.delete("/{feedback_id}", response_model=MessageFeedbackResponse)
async def delete_message_feedback(feedback_id: str, db: AsyncSession = Depends(get_db)):
    message_feedback_service = MessageFeedbackService(db)
    message_feedback = await message_feedback_service.delete_message_feedback(
        feedback_id
    )
    if not message_feedback:
        raise HTTPException(status_code=404, detail="Message feedback not found")
    return message_feedback
