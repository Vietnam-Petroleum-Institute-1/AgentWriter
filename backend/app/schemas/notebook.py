from typing import Optional

from pydantic import BaseModel


class NotebookBase(BaseModel):
    title: str


class NotebookCreate(NotebookBase):
    pass


class NotebookUpdate(NotebookBase):
    pass


class NotebookResponse(NotebookBase):
    notebook_id: str
    user_id: str

    class Config:
        orm_mode = True
