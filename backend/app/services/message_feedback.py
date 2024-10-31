from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.message_feedback import MessageFeedback
from app.schemas.message_feedback import MessageFeedbackCreate, MessageFeedbackUpdate


class MessageFeedbackService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_message_feedback(
        self, feedback_in: MessageFeedbackCreate, user_id: str
    ) -> MessageFeedback:
        feedback = MessageFeedback(**feedback_in.dict(), user_id=user_id)
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    async def get_message_feedbacks(
        self, skip: int = 0, limit: int = 100
    ) -> List[MessageFeedback]:
        result = await self.db.execute(
            select(MessageFeedback).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_message_feedback(self, feedback_id: str) -> Optional[MessageFeedback]:
        result = await self.db.execute(
            select(MessageFeedback).where(MessageFeedback.feedback_id == feedback_id)
        )
        return result.scalar_one_or_none()

    async def update_message_feedback(
        self, feedback_id: str, feedback_in: MessageFeedbackUpdate
    ) -> Optional[MessageFeedback]:
        feedback = await self.get_message_feedback(feedback_id)
        if not feedback:
            return None

        for field, value in feedback_in.dict(exclude_unset=True).items():
            setattr(feedback, field, value)

        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    async def delete_message_feedback(
        self, feedback_id: str
    ) -> Optional[MessageFeedback]:
        feedback = await self.get_message_feedback(feedback_id)
        if not feedback:
            return None

        await self.db.delete(feedback)
        await self.db.commit()
        return feedback
