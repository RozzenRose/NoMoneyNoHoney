from fastapi import APIRouter
from fastapi import Depends, status, HTTPException
from typing import Annotated
from app.database.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.functions.auth_functions import get_current_user
from app.schemas import PurchasesListCreate, PurchaseTimeLimits
from app.database.db_functions import (create_purchases_list_in_db, get_all_purchases_from_db,
                                        get_purchases_current_week_from_db, get_purchases_in_limits_from_db)


router = APIRouter(prefix='/purchases', tags=['purchases'])


@router.post('/new_purchases')
async def new_list_purchases(db: Annotated[AsyncSession, Depends(get_db)],
                             purchases: PurchasesListCreate,
                             user: Annotated[dict, Depends(get_current_user)]):
    await create_purchases_list_in_db(db, purchases, user.get('user_id'))
    return {'status_code': status.HTTP_201_CREATED,
            'transaction': 'Purchase created successfully'}


@router.get('/all_purchases')
async def get_all_purchases(db: Annotated[AsyncSession, Depends(get_db)],
                            user: Annotated[dict, Depends(get_current_user)]):
    answer = await get_all_purchases_from_db(db, user.get('user_id'))
    return {'purchases': answer}


@router.get('/last_7_days_purchases')
async def get_last_7_days_purchases(db: Annotated[AsyncSession, Depends(get_db)],
                                     user: Annotated[dict, Depends(get_current_user)]):
    answer = await get_purchases_current_week_from_db(db, user.get('user_id'))
    return {'purchases': answer}


@router.get('/purchases_limits')
async def get_purchases_in_limits(db: Annotated[AsyncSession, Depends(get_db)],
                                  user: Annotated[dict, Depends(get_current_user)],
                                  date_limits: Annotated[PurchaseTimeLimits, Depends()]):
    answer = await get_purchases_in_limits_from_db(db, user.get('user_id'),
                                                  date_limits.start_date,
                                                  date_limits.end_date)
    return {'purchases': answer}
