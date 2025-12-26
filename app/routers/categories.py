from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from app.database.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.functions.auth_functions import get_current_user
from app.database.db_functions import (get_all_categories_from_db, create_category_in_db,
                                       delete_categories_from_db)


router = APIRouter(prefix='/categories', tags=['categories'])


@router.post('/new_category', status_code=status.HTTP_201_CREATED)
async def create_category(db: Annotated[AsyncSession, Depends(get_db)], category_name,
                          user: Annotated[dict, Depends(get_current_user)]):
    await create_category_in_db(db, user.get('user_id'), category_name)
    return {'status_code':status.HTTP_201_CREATED,
            'transaction': 'Category created successfully'}


@router.get('/all_your_categories')
async def get_all_categories(db: Annotated[AsyncSession, Depends(get_db)],
                             user: Annotated[dict, Depends(get_current_user)]):
    answer = await get_all_categories_from_db(db, user.get('user_id'))
    return {'categories': answer}

@router.delete('/delete_categories')
async def delete_categories(db: Annotated[AsyncSession, Depends(get_db)],
                            user: Annotated[dict, Depends(get_current_user)],
                            categories_id: list[int]):
    await delete_categories_from_db(db, user.get('user_id'), categories_id)