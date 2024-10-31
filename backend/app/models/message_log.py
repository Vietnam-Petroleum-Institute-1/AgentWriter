from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class MessageLog(BaseModel):
    __tablename__ = "message_log"

    message_id = Column(
        String(100), primary_key=True, default=lambda: BaseModel.generate_id("message")
    )
    notebook_id = Column(
        String(100),
        ForeignKey("notebook.notebook_id", ondelete="CASCADE"),
        nullable=False,
        name="fk_message_notebook_id",
    )
    bot_id = Column(
        String(100),
        ForeignKey("bot.bot_id", ondelete="CASCADE"),
        nullable=False,
        name="fk_message_bot_id",
    )
    content = Column(Text, nullable=False)
    from_user = Column(Boolean, nullable=False)

    notebook = relationship("Notebook", backref="messages")
    bot = relationship("Bot", backref="messages")
