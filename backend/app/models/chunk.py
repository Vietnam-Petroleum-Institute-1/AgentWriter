from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Chunk(BaseModel):
    chunk_id = Column(
        String(100), primary_key=True, default=lambda: BaseModel.generate_id("chunk")
    )
    content = Column(Text, nullable=False)
    file_id = Column(
        String(100),
        ForeignKey("file.file_id", ondelete="CASCADE", name="fk_chunk_file_id"),
        nullable=False,
    )

    file = relationship("File", backref="chunks")
