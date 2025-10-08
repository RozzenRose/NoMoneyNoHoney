from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from app.database.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import CreateIncome, IncomeTimeLimits
from app.database.db_functions import (create_income_in_db, get_all_incomes_from_db,
                                       get_incomes_current_from_db, get_incomes_last_month_from_db,
                                       get_incomes_in_time_limits_from_db)
from app.functions.auth_functions import get_current_user
from app.rabbitmq import rpc_incomes_request
import asyncio, json


router = APIRouter(prefix='/incomes', tags=['incomes'])


@router.post('/new_income', status_code=status.HTTP_201_CREATED)
async def create_income(db: Annotated[AsyncSession, Depends(get_db)],
                        income: CreateIncome,
                        user: Annotated[dict, Depends(get_current_user)]):
    await create_income_in_db(db, user.get('user_id'), income.description, income.quantity,
                              income.currency)
    return {'status_code':status.HTTP_201_CREATED,
            'transaction': 'Income created successfully'}


@router.get('/all_your_incomes')
async def get_all_incomes(db: Annotated[AsyncSession, Depends(get_db)],
                          user: Annotated[dict, Depends(get_current_user)],
                          current: str | None = None):
    if current not in ('EUR', 'RUB', 'RSD', None):
        raise HTTPException(status_code=400, detail="Currency error: choose only EUR/RUB/RSD or leave this field blank")
    future = asyncio.get_running_loop().create_future()
    raw_data = await get_all_incomes_from_db(db, user.get('user_id'))
    reply_queue, consumer_tag = await rpc_incomes_request(future, raw_data, current)

    try:
        response = json.loads(await asyncio.wait_for(future, timeout=10))  # ждем ответа
        # возвращаем ответ юзеру
        return {'incomes': raw_data} | response
    except asyncio.TimeoutError:
        return {'incomes': raw_data,
                'euro': "CurrentAggregator doesn't response",
                'rub': "CurrentAggregator doesn't response",
                'rsd': "CurrentAggregator doesn't response",
                'answer': "CurrentAggregator doesn't response"}
    finally:
        await reply_queue.cancel(consumer_tag)  # сворачиваем канал


@router.get('/incomes_current_month')
async def get_incomes_current_month(db: Annotated[AsyncSession, Depends(get_db)],
                                    user: Annotated[dict, Depends(get_current_user)],
                                    current: str | None = None):
    if current not in ('EUR', 'RUB', 'RSD', None):
        raise HTTPException(status_code=400, detail="Currency error: choose only EUR/RUB/RSD or leave this field blank")
    future = asyncio.get_running_loop().create_future()
    raw_data = await get_incomes_current_from_db(db, user.get('user_id'))
    reply_queue, consumer_tag = await rpc_incomes_request(future, raw_data, current)

    try:
        response = json.loads(await asyncio.wait_for(future, timeout=10))
        return {'incomes': raw_data} | response
    except asyncio.TimeoutError:
        return {'incomes': raw_data,
                'euro': "CurrentAggregator doesn't response",
                'rub': "CurrentAggregator doesn't response",
                'rsd': "CurrentAggregator doesn't response",
                'answer': "CurrentAggregator doesn't response"}
    finally:
        await reply_queue.cancel(consumer_tag)



@router.get('/incomes_last_month')
async def get_incomes_last_month(db: Annotated[AsyncSession, Depends(get_db)],
                                 user: Annotated[dict, Depends(get_current_user)],
                                 current: str | None = None):
    if current not in ('EUR', 'RUB', 'RSD', None):
        raise HTTPException(status_code=400, detail="Currency error: choose only EUR/RUB/RSD or leave this field blank")
    future = asyncio.get_running_loop().create_future()
    raw_data = await get_incomes_last_month_from_db(db, user.get('user_id'))
    reply_queue, consumer_tag = await rpc_incomes_request(future, raw_data, current)

    try:
        response = json.loads(await asyncio.wait_for(future, timeout=10))
        return {'incomes': raw_data} | response
    except asyncio.TimeoutError:
        return {'incomes': raw_data,
                'euro': "CurrentAggregator doesn't response",
                'rub': "CurrentAggregator doesn't response",
                'rsd': "CurrentAggregator doesn't response",
                'answer': "CurrentAggregator doesn't response"}
    finally:
        await reply_queue.cancel(consumer_tag)


@router.get('/incomes_limits')
async def get_incomes_in_time_limits(db: Annotated[AsyncSession, Depends(get_db)],
                                     user: Annotated[dict, Depends(get_current_user)],
                                     date_limits: IncomeTimeLimits = Depends(),
                                     current: str | None = None):
    if current not in ('EUR', 'RUB', 'RSD', None):
        raise HTTPException(status_code=400, detail="Currency error: choose only EUR/RUB/RSD or leave this field blank")
    future = asyncio.get_running_loop().create_future()
    raw_data = await get_incomes_in_time_limits_from_db(db, user.get('user_id'),
                                                       date_limits.start_date,
                                                       date_limits.end_date)
    reply_queue, consumer_tag = await rpc_incomes_request(future, raw_data, current)

    try:
        response = json.loads(await asyncio.wait_for(future, timeout=10))
        return {'incomes': raw_data} | response
    except asyncio.TimeoutError:
        return {'incomes': raw_data,
                'euro': "CurrentAggregator doesn't response",
                'rub': "CurrentAggregator doesn't response",
                'rsd': "CurrentAggregator doesn't response",
                'answer': "CurrentAggregator doesn't response"}
    finally:
        await reply_queue.cancel(consumer_tag)