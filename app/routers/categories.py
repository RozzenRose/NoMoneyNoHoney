from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from app.database.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import CreateCategory


router = APIRouter(prefix='/categories', tags=['categories'])


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_category(db: Annotated[AsyncSession, Depends(get_db)], create_category: CreateCategory):
    if create_category.parent_id_category is not None:
        pass
