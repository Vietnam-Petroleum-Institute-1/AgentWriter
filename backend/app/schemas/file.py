from pydantic import BaseModel

class FileData(BaseModel):
    file_id: str
    user_id: str
    session_id: str
    conversation_id: str
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    created_by: str
