from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from app.database.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.functions.auth_functions import get_current_user
from app.schemas import PurchasesListCreate, PurchaseTimeLimits
from app.database.db_functions import (create_purchases_list_in_db, get_all_purchases_from_db,
                                get_purchases_current_week_from_db, get_purchases_in_limits_from_db)
from app.rabbitmq import rpc_puchases_request
import asyncio, json


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
                            user: Annotated[dict, Depends(get_current_user)],
                            current: str | None = None):
    if current not in ('EUR', 'RUB', 'RSD', None):
        raise HTTPException(status_code=400, detail="Currency error: choose only EUR/RUB/RSD or leave this field blank")
    future = asyncio.get_running_loop().create_future()
    raw_data = await get_all_purchases_from_db(db, user.get('user_id'))
    reply_queue, consumer_tag = await rpc_puchases_request(future, raw_data, current)

    try:
        response = json.loads(await asyncio.wait_for(future, timeout=10))  # ждем ответа
        return {'purchases': raw_data} | response
    except asyncio.TimeoutError:
        return {'purchases': raw_data,
                'euro': "CurrentAggregator doesn't response",
                'rub': "CurrentAggregator doesn't response",
                'rsd': "CurrentAggregator doesn't response",
                'answer': "CurrentAggregator doesn't response"}
    finally:
        await reply_queue.cancel(consumer_tag)  # сворачиваем канал



@router.get('/last_7_days_purchases')
async def get_last_7_days_purchases(db: Annotated[AsyncSession, Depends(get_db)],
                                     user: Annotated[dict, Depends(get_current_user)],
                                     current: str | None = None):
    if current not in ('EUR', 'RUB', 'RSD', None):
        raise HTTPException(status_code=400, detail="Currency error: choose only EUR/RUB/RSD or leave this field blank")
    future = asyncio.get_running_loop().create_future()
    raw_data = await get_purchases_current_week_from_db(db, user.get('user_id'))
    reply_queue, consumer_tag = await rpc_puchases_request(future, raw_data, current)

    try:
        response = json.loads(await asyncio.wait_for(future, timeout=10))  # ждем ответа
        return {'purchases': raw_data} | response
    except asyncio.TimeoutError:
        return {'purchases': raw_data,
                'euro': "CurrentAggregator doesn't response",
                'rub': "CurrentAggregator doesn't response",
                'rsd': "CurrentAggregator doesn't response",
                'answer': "CurrentAggregator doesn't response"}
    finally:
        await reply_queue.cancel(consumer_tag)  # сворачиваем канал


@router.get('/purchases_limits')
async def get_purchases_in_limits(db: Annotated[AsyncSession, Depends(get_db)],
                                  user: Annotated[dict, Depends(get_current_user)],
                                  date_limits: Annotated[PurchaseTimeLimits, Depends()],
                                  current: str | None = None):
    if current not in ('EUR', 'RUB', 'RSD', None):
        raise HTTPException(status_code=400, detail="Currency error: choose only EUR/RUB/RSD or leave this field blank")
    future = asyncio.get_running_loop().create_future()
    raw_data = await get_purchases_in_limits_from_db(db, user.get('user_id'),
                                                   date_limits.start_date,
                                                   date_limits.end_date)
    reply_queue, consumer_tag = await rpc_puchases_request(future, raw_data, current)

    try:
        response = json.loads(await asyncio.wait_for(future, timeout=10))  # ждем ответа
        return {'purchases': raw_data} | response
    except asyncio.TimeoutError:
        return {'purchases': raw_data,
                'euro': "CurrentAggregator doesn't response",
                'rub': "CurrentAggregator doesn't response",
                'rsd': "CurrentAggregator doesn't response",
                'answer': "CurrentAggregator doesn't response"}
    finally:
        await reply_queue.cancel(consumer_tag)  # сворачиваем канал
