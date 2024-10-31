from sqlalchemy import Column, String

from app.models.base import BaseModel


class Bot(BaseModel):
    bot_id = Column(
        String(100), primary_key=True, default=lambda: BaseModel.generate_id("bot")
    )
    name = Column(String(100), nullable=False)
    type = Column(String(100), nullable=False)
