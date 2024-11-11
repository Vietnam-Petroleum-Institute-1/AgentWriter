from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class File(BaseModel):
    __tablename__ = "file"

    file_id = Column(
        String(100), primary_key=True, default=lambda: BaseModel.generate_id("file")
    )
    notebook_id = Column(
        String(100),
        ForeignKey(
            "notebook.notebook_id", ondelete="CASCADE", name="fk_file_notebook_id"
        ),
        nullable=False,
    )
    user_id = Column(
        String(100),
        ForeignKey("user.user_id", ondelete="CASCADE", name="fk_file_user_id"),
        nullable=False,
    )
    session_id = Column(String(100), nullable=True)
    file_size = Column(Integer, nullable=True)
    updated_by = Column(String(100), nullable=True)
    file_name = Column(String(255), nullable=False)
    extension = Column(
        Enum("pdf", "docx", "txt", name="file_extension_enum"), nullable=False
    )
    summary = Column(Text)
    content = Column(Text)
    file_path = Column(String(255), nullable=False)

    notebook = relationship("Notebook", backref="files")
