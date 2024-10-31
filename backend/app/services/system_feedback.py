from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.system_feedback import SystemFeedback
from app.schemas.system_feedback import SystemFeedbackCreate, SystemFeedbackUpdate


class SystemFeedbackService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_system_feedback(
        self, feedback_in: SystemFeedbackCreate, user_id: str
    ) -> SystemFeedback:
        feedback = SystemFeedback(**feedback_in.dict(), user_id=user_id)
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    async def get_system_feedbacks(
        self, skip: int = 0, limit: int = 100
    ) -> List[SystemFeedback]:
        result = await self.db.execute(select(SystemFeedback).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_system_feedback(self, feedback_id: str) -> Optional[SystemFeedback]:
        result = await self.db.execute(
            select(SystemFeedback).where(SystemFeedback.feedback_id == feedback_id)
        )
        return result.scalar_one_or_none()

    async def update_system_feedback(
        self, feedback_id: str, feedback_in: SystemFeedbackUpdate
    ) -> Optional[SystemFeedback]:
        feedback = await self.get_system_feedback(feedback_id)
        if not feedback:
            return None

        for field, value in feedback_in.dict(exclude_unset=True).items():
            setattr(feedback, field, value)

        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    async def delete_system_feedback(
        self, feedback_id: str
    ) -> Optional[SystemFeedback]:
        feedback = await self.get_system_feedback(feedback_id)
        if not feedback:
            return None

        await self.db.delete(feedback)
        await self.db.commit()
        return feedback
