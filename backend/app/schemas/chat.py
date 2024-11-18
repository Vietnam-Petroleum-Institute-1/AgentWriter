from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ChatMessage(BaseModel):
    user_message: str
    file_id: str
    user_id: str


class ChatResponse(BaseModel):
    final_result: str
    conversation_id: Optional[str]
    message_id: Optional[str]


class FileUploadResponse(BaseModel):
    message: str
    file_id: str


class MessageLogCreate(BaseModel):
    notebook_id: str
    bot_id: str
    content: str
    from_user: bool


class MessageLogResponse(BaseModel):
    message_id: str
    notebook_id: str
    bot_id: str
    content: str
    from_user: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UpdateSegmentRequest(BaseModel):
    segment_id: str
    content: str


class UpdateSegmentResponse(BaseModel):
    message: str
    success: bool
