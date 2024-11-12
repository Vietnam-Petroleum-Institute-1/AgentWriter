from typing import List, Optional

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


class FileResponse(BaseModel):
    file_id: str
    file_name: str
    extension: str
    file_size: int | None
    summary: str | None
    file_path: str

    class Config:
        from_attributes = True


class NotebookWithFilesResponse(BaseModel):
    notebook_id: str
    title: str
    conversation_dify_id: str | None
    files: List[FileResponse]

    class Config:
        from_attributes = True
