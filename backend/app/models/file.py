from sqlalchemy import Column, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class File(BaseModel):
    file_id = Column(
        String(100), primary_key=True, default=lambda: BaseModel.generate_id("file")
    )
    notebook_id = Column(
        String(100),
        ForeignKey("notebook.notebook_id", ondelete="CASCADE"),
        nullable=False,
        name="fk_file_notebook_id",
    )
    file_name = Column(String(255), nullable=False)
    extension = Column(
        Enum("pdf", "docx", "txt", name="file_extension_enum"), nullable=False
    )
    summary = Column(Text)
    content = Column(Text)
    file_path = Column(String(255), nullable=False)

    notebook = relationship("Notebook", backref="files")
