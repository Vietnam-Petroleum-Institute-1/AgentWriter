from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class UserResponse(UserBase):
    user_id: str
    role: str

    class Config:
        from_attributes = True
