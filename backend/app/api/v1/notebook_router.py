from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_token
from app.models.notebook import Notebook
from app.models.user import User
from app.schemas.notebook import NotebookCreate, NotebookResponse, NotebookUpdate
from app.services.notebook import NotebookService

router = APIRouter(prefix="/notebooks", tags=["Notebooks"])


@router.post("", response_model=NotebookResponse)
async def create_notebook(
    notebook_in: NotebookCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verify_token),
):
    notebook_service = NotebookService(db)
    notebook = await notebook_service.create_notebook(notebook_in, user_id)
    return notebook


@router.get("", response_model=List[NotebookResponse])
async def read_notebooks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verify_token),
):
    notebook_service = NotebookService(db)
    notebooks = await notebook_service.get_user_notebooks(
        user_id, skip=skip, limit=limit
    )
    return notebooks


@router.get(
    "/{notebook_id}",
    response_model=NotebookResponse,
    dependencies=[Depends(verify_token)],
)
async def read_notebook(notebook_id: str, db: AsyncSession = Depends(get_db)):
    notebook_service = NotebookService(db)
    notebook = await notebook_service.get_notebook(notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return notebook


@router.put(
    "/{notebook_id}",
    response_model=NotebookResponse,
    dependencies=[Depends(verify_token)],
)
async def update_notebook(
    notebook_id: str, notebook_in: NotebookUpdate, db: AsyncSession = Depends(get_db)
):
    notebook_service = NotebookService(db)
    notebook = await notebook_service.update_notebook(notebook_id, notebook_in)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return notebook


@router.delete(
    "/{notebook_id}",
    response_model=NotebookResponse,
    dependencies=[Depends(verify_token)],
)
async def delete_notebook(notebook_id: str, db: AsyncSession = Depends(get_db)):
    notebook_service = NotebookService(db)
    notebook = await notebook_service.delete_notebook(notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return notebook
