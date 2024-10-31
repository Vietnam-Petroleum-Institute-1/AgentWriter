from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.schemas.auth import Token, UserCreate, UserLogin
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
async def login(
    user: UserLogin, response: Response, db: AsyncSession = Depends(get_db)
) -> Token:
    auth_service = AuthService(db)
    user = await auth_service.authenticate(user.username, user.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Set HTTP-only cookie to store refresh token
    refresh_token = create_refresh_token(user.user_id, role=user.role)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True if using HTTPS
        samesite="lax",
    )

    return Token(access_token=create_access_token(user.user_id, user.role))


@router.post("/register", response_model=Token)
async def register(
    user_in: UserCreate, response: Response, db: AsyncSession = Depends(get_db)
) -> Token:
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = await auth_service.create_user(user_in=user_in)
    refresh_token = create_refresh_token(user.user_id, role=user.role)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return Token(access_token=create_access_token(user.user_id, user.role))


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    response: Response,
    refresh_token: str = Cookie(None),
) -> Token:
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token provided")

    # Decode the refresh token to get the payload
    try:
        payload = decode_refresh_token(refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload["user_id"]
    role = payload["role"]
    exp = payload["exp"]

    # Create a new access token
    new_access_token = create_access_token(user_id=user_id, role=role)

    # Optionally create a new refresh token
    new_refresh_token = create_refresh_token(user_id=user_id, role=role, exp=exp)

    # Set the new refresh token in the HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,  # Set to True if using HTTPS
        samesite="lax",
    )

    return Token(access_token=new_access_token)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}
