from typing import Optional

from pydantic import BaseModel


class MessageFeedbackBase(BaseModel):
    user_id: str
    message_id: str
    notebook_id: str
    content: str
    seen: bool = False


class MessageFeedbackCreate(MessageFeedbackBase):
    pass


class MessageFeedbackUpdate(MessageFeedbackBase):
    pass


class MessageFeedbackResponse(MessageFeedbackBase):
    feedback_id: str

    class Config:
        orm_mode = True
