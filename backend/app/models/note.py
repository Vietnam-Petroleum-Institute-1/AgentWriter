from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Note(BaseModel):
    note_id = Column(
        String(100), primary_key=True, default=lambda: BaseModel.generate_id("note")
    )
    notebook_id = Column(
        String(100),
        ForeignKey("notebook.notebook_id", ondelete="CASCADE"),
        nullable=False,
        name="fk_note_notebook_id",
    )
    chunk_id = Column(
        String(100),
        ForeignKey("chunk.chunk_id", ondelete="CASCADE"),
        nullable=False,
        name="fk_note_chunk_id",
    )
    title = Column(String(255), nullable=False)
    content = Column(Text)

    notebook = relationship("Notebook", backref="notes")
    chunk = relationship("Chunk", backref="notes")
