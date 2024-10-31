from sqlalchemy import Column, Enum, String

from app.models.base import BaseModel


class User(BaseModel):
    user_id = Column(
        String(100), primary_key=True, default=lambda: BaseModel.generate_id("user")
    )
    username = Column(String(100), nullable=False, unique=True)
    full_name = Column(String(255))
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role = Column(
        Enum("admin", "user", name="user_role_enum"), nullable=False, default="user"
    )
