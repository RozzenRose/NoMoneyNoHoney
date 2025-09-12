from fastapi import APIRouter
from fastapi import Depends, status, HTTPException
from typing import Annotated
from app.database.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.functions.auth_functions import get_current_user
from app.schemas import PurchasesListCreate
from app.database.db_functions import create_purchases_list_in_db


router = APIRouter(prefix='/purchases', tags=['purchases'])


@router.post('/new_purchases')
async def new_list_purchases(db: Annotated[AsyncSession, Depends(get_db)],
                             purchases: PurchasesListCreate,
                             user: Annotated[dict, Depends(get_current_user)]):
    await create_purchases_list_in_db(db, purchases, user.get('user_id'))
    return {'status_code': status.HTTP_201_CREATED,
            'transaction': 'Purchase created successfully'}
