from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import admin_required
from app.schemas.user import UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.put(
    "/{user_id}", response_model=UserResponse, dependencies=[Depends(admin_required)]
)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.update_user(user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete(
    "/{user_id}", response_model=UserResponse, dependencies=[Depends(admin_required)]
)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.delete_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
