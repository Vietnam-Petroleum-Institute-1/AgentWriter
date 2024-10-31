from typing import Optional

from pydantic import BaseModel


class NoteBase(BaseModel):
    title: str
    content: Optional[str] = None
    notebook_id: str
    chunk_id: str


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    pass


class NoteResponse(NoteBase):
    note_id: str
    user_id: str

    class Config:
        orm_mode = True
