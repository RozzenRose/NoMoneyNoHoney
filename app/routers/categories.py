from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from app.database.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import CreateCategory
from app.database.db_functions import create_category_in_db


router = APIRouter(prefix='/categories', tags=['categories'])


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_category(db: Annotated[AsyncSession, Depends(get_db)], create_category: CreateCategory):
    await create_category_in_db(db, create_category.owner_id, create_category.category_name)
    return {'status_code':status.HTTP_201_CREATED,
            'transaction': 'Category created successfully'}
