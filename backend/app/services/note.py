from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi.responses import StreamingResponse
from io import BytesIO
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate
from fastapi.responses import FileResponse

class NoteService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_note(self, note_in: NoteCreate) -> Note:
        note = Note(**note_in.model_dump())
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def get_notes(
        self, notebook_id: str, skip: int = 0, limit: int = 100
    ) -> List[Note]:
        result = await self.db.execute(
            select(Note)
            .filter(Note.notebook_id == notebook_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_note(self, note_id: str) -> Optional[Note]:
        result = await self.db.execute(select(Note).filter(Note.note_id == note_id))
        return result.scalar_one_or_none()

    async def update_note(self, note_id: str, note_in: NoteUpdate) -> Optional[Note]:
        note = await self.get_note(note_id)
        if not note:
            return None

        for field, value in note_in.model_dump(exclude_unset=True).items():
            setattr(note, field, value)

        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def delete_note(self, note_id: str) -> Optional[Note]:
        note = await self.get_note(note_id)
        if not note:
            return None

        await self.db.delete(note)
        await self.db.commit()
        return note
    
    async def generate_markdown_content(self,node_ids: List[str]) -> str:
        result = await self.db.execute(
            select(Note).filter(Note.note_id.in_(node_ids))
        )
        notes = result.scalars().all()

        if not notes:
            raise ValueError("No notes found for this notebook_id.")

        # Gen Markdown
        markdown_content = "# Notebook Content\n\n"
        for note in notes:
            markdown_content += f"## {note.title}\n\n"
            markdown_content += f"{note.content}\n\n"

        return markdown_content


    async def download_markdown(self, node_ids: List[str]) -> FileResponse:
        # Create a .md file to download
        markdown_content = await self.generate_markdown_content(node_ids)

        # Tạo stream từ nội dung Markdown
        buffer = BytesIO(markdown_content.encode("utf-8"))
        filename = f"notebook_{node_ids[0]}.md"

        # Trả về nội dung dưới dạng StreamingResponse
        return StreamingResponse(
            buffer,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )