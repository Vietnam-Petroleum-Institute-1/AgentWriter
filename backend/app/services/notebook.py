from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.notebook import Notebook
from app.schemas.notebook import NotebookCreate, NotebookUpdate


class NotebookService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notebook(
        self, notebook_in: NotebookCreate, user_id: str
    ) -> Notebook:
        notebook = Notebook(**notebook_in.dict(), user_id=user_id)
        self.db.add(notebook)
        await self.db.commit()
        await self.db.refresh(notebook)
        return notebook

    async def get_notebooks(self, skip: int = 0, limit: int = 100) -> List[Notebook]:
        result = await self.db.execute(select(Notebook).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_notebook(self, notebook_id: str) -> Optional[Notebook]:
        result = await self.db.execute(
            select(Notebook).filter(Notebook.notebook_id == notebook_id)
        )
        return result.scalar_one_or_none()

    async def get_user_notebooks(
        self, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Notebook]:
        result = await self.db.execute(
            select(Notebook)
            .filter(Notebook.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update_notebook(
        self, notebook_id: str, notebook_in: NotebookUpdate
    ) -> Optional[Notebook]:
        notebook = await self.get_notebook(notebook_id)
        if not notebook:
            return None

        for field, value in notebook_in.dict(exclude_unset=True).items():
            setattr(notebook, field, value)

        await self.db.commit()
        await self.db.refresh(notebook)
        return notebook

    async def delete_notebook(self, notebook_id: str) -> Optional[Notebook]:
        notebook = await self.get_notebook(notebook_id)
        if not notebook:
            return None

        await self.db.delete(notebook)
        await self.db.commit()
        return notebook
