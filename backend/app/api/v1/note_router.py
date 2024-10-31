from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate
from app.services.note import NoteService

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post("/", response_model=NoteResponse)
async def create_note(
    note_in: NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note_service = NoteService(db)
    note = await note_service.create_note(note_in, current_user.user_id)
    return note


@router.get("/", response_model=List[NoteResponse])
async def read_notes(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    note_service = NoteService(db)
    notes = await note_service.get_notes(skip=skip, limit=limit)
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
async def read_note(note_id: str, db: AsyncSession = Depends(get_db)):
    note_service = NoteService(db)
    note = await note_service.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str, note_in: NoteUpdate, db: AsyncSession = Depends(get_db)
):
    note_service = NoteService(db)
    note = await note_service.update_note(note_id, note_in)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.delete("/{note_id}", response_model=NoteResponse)
async def delete_note(note_id: str, db: AsyncSession = Depends(get_db)):
    note_service = NoteService(db)
    note = await note_service.delete_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note
