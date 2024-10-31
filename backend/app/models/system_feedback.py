from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class SystemFeedback(BaseModel):
    feedback_id = Column(
        String(100),
        primary_key=True,
        default=lambda: BaseModel.generate_id("sysfeedback"),
    )
    user_id = Column(
        String(100),
        ForeignKey("user.user_id", ondelete="CASCADE"),
        nullable=False,
        name="fk_sysfeedback_user_id",
    )
    content = Column(Text, nullable=False)
    seen = Column(Boolean, nullable=False, default=False)

    user = relationship("User", backref="system_feedbacks")
