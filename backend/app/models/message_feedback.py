from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class MessageFeedback(BaseModel):
    __tablename__ = "message_feedback"

    feedback_id = Column(
        String(100), primary_key=True, default=lambda: BaseModel.generate_id("feedback")
    )
    user_id = Column(
        String(100),
        ForeignKey("user.user_id", ondelete="CASCADE", name="fk_feedback_user_id"),
        nullable=False,
    )
    message_id = Column(
        String(100),
        ForeignKey(
            "message_log.message_id", ondelete="CASCADE", name="fk_feedback_message_id"
        ),
        nullable=False,
    )
    notebook_id = Column(
        String(100),
        ForeignKey(
            "notebook.notebook_id", ondelete="CASCADE", name="fk_feedback_notebook_id"
        ),
        nullable=False,
    )
    content = Column(Text, nullable=False)
    seen = Column(Boolean, nullable=False, default=False)

    user = relationship("User", backref="message_feedbacks")
    message = relationship("MessageLog", backref="feedbacks")
    notebook = relationship("Notebook", backref="message_feedbacks")
