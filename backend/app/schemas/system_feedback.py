from typing import Optional

from pydantic import BaseModel


class SystemFeedbackBase(BaseModel):
    content: str


class SystemFeedbackCreate(SystemFeedbackBase):
    pass


class SystemFeedbackUpdate(SystemFeedbackBase):
    pass


class SystemFeedbackResponse(SystemFeedbackBase):
    user_id: str
    feedback_id: str
    seen: bool

    class Config:
        orm_mode = True
