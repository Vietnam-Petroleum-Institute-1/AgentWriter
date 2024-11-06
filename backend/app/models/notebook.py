from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Notebook(BaseModel):
    notebook_id = Column(
        String(100), primary_key=True, default=lambda: BaseModel.generate_id("notebook")
    )
    user_id = Column(
        String(100),
        ForeignKey("user.user_id", ondelete="CASCADE", name="fk_notebook_user_id"),
        nullable=False,
    )
    title = Column(String(255), nullable=False)

    user = relationship("User", backref="notebooks")
