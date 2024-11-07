from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_token
from app.models.user import User
from app.schemas.user import PasswordChange, UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    return current_user


@router.get(
    "/{user_id}", response_model=UserResponse, dependencies=[Depends(verify_token)]
)
async def read_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get(
    "/", response_model=List[UserResponse], dependencies=[Depends(verify_token)]
)
async def read_users(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    users = await user_service.get_users(skip=skip, limit=limit)
    return users


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_in: UserUpdate,
    user_id: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.update_user(user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChange,
    user_id: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    await user_service.change_password(
        user_id=user_id,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
    )
    return {"message": "Password updated successfully"}
