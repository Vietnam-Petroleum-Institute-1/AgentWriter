from typing import Optional

from pydantic import BaseModel


class SystemFeedbackBase(BaseModel):
    user_id: str
    content: str
    seen: bool = False


class SystemFeedbackCreate(SystemFeedbackBase):
    pass


class SystemFeedbackUpdate(SystemFeedbackBase):
    pass


class SystemFeedbackResponse(SystemFeedbackBase):
    feedback_id: str

    class Config:
        orm_mode = True
