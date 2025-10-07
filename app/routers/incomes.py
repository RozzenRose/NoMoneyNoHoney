from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from app.database.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import CreateIncome, IncomeTimeLimits
from app.database.db_functions import (create_income_in_db, get_all_incomes_from_db,
                                       get_incomes_current_from_db, get_incomes_last_month_from_db,
                                       get_incomes_in_time_limits_from_db)
from app.functions.auth_functions import get_current_user
from app.rabbitmq import RabbitMQConnectionManager, consume_response, send_message
import asyncio, uuid, json


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
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    correlation_id = str(uuid.uuid4())  # создаем уникальный id для сообщения
    channel = await RabbitMQConnectionManager.get_channel()
    queue = await channel.declare_queue('api_aggregation_queue', durable=True)
    reply_queue = await channel.declare_queue('reply_api_aggregation_queue', durable=True)
    consumer_tag = await consume_response(reply_queue, correlation_id, future)
    answer = await get_all_incomes_from_db(db, user.get('user_id'))
    if current not in ('EUR', 'RUB', 'RSD', None):
        raise HTTPException(status_code=400, detail="Currency error: choose only EUR/RUB/RSD or leave this field blank")
    data = {'incomes': [item.to_dict() for item in answer], 'current_currency': current, 'content': 'Incomes'}
    await send_message(channel, json.dumps(data).encode(), queue, reply_queue, correlation_id)

    try:
        response = json.loads(await asyncio.wait_for(future, timeout=10)) #ждем ответа
        #возвращаем ответ юзеру
        return {'incomes': answer} | response
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout") #если ответ не пришел выдаем таймаут
    finally:
        await reply_queue.cancel(consumer_tag) #сворачиваем канал


@router.get('/incomes_current_month')
async def get_incomes_current_month(db: Annotated[AsyncSession, Depends(get_db)],
                                    user: Annotated[dict, Depends(get_current_user)],
                                    current: str | None = None):
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    correlation_id = str(uuid.uuid4())  # создаем уникальный id для сообщения
    channel = await RabbitMQConnectionManager.get_channel()
    queue = await channel.declare_queue('api_aggregation_queue', durable=True)
    reply_queue = await channel.declare_queue('reply_api_aggregation_queue', durable=True)
    consumer_tag = await consume_response(reply_queue, correlation_id, future)
    answer = await get_incomes_current_from_db(db, user.get('user_id'))
    if current not in ('EUR', 'RUB', 'RSD', None):
        raise HTTPException(status_code=400, detail="Currency error: choose only EUR/RUB/RSD or leave this field blank")
    data = {
        'incomes': [item.to_dict() for item in answer],
        'current_currency': current,
        'content': 'Incomes'
    }
    await send_message(channel, json.dumps(data).encode(), queue, reply_queue, correlation_id)

    try:
        response = json.loads(await asyncio.wait_for(future, timeout=10)) #ждем ответа
        #возвращаем ответ юзеру
        return {'incomes': answer} | response
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout") #если ответ не пришел выдаем таймаут
    finally:
        await reply_queue.cancel(consumer_tag) #сворачиваем канал



@router.get('/incomes_last_month')
async def get_incomes_last_month(db: Annotated[AsyncSession, Depends(get_db)],
                                 user: Annotated[dict, Depends(get_current_user)],
                                 current: str | None = None):
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    correlation_id = str(uuid.uuid4())  # создаем уникальный id для сообщения
    channel = await RabbitMQConnectionManager.get_channel()
    queue = await channel.declare_queue('api_aggregation_queue', durable=True)
    reply_queue = await channel.declare_queue('reply_api_aggregation_queue', durable=True)
    consumer_tag = await consume_response(reply_queue, correlation_id, future)
    answer = await get_incomes_last_month_from_db(db, user.get('user_id'))
    if current not in ('EUR', 'RUB', 'RSD', None):
        raise HTTPException(status_code=400, detail="Currency error: choose only EUR/RUB/RSD or leave this field blank")
    data = {
        'incomes': [item.to_dict() for item in answer],
        'current_currency': current,
        'content': 'Incomes'
    }
    await send_message(channel, json.dumps(data).encode(), queue, reply_queue, correlation_id)

    try:
        response = json.loads(await asyncio.wait_for(future, timeout=10)) #ждем ответа
        #возвращаем ответ юзеру
        return {'incomes': answer} | response
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout") #если ответ не пришел выдаем таймаут
    finally:
        await reply_queue.cancel(consumer_tag) #сворачиваем канал


@router.get('/incomes_limits')
async def get_incomes_in_time_limits(db: Annotated[AsyncSession, Depends(get_db)],
                                     user: Annotated[dict, Depends(get_current_user)],
                                     date_limits: IncomeTimeLimits = Depends(),
                                     current: str | None = None):
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    correlation_id = str(uuid.uuid4())  # создаем уникальный id для сообщения
    channel = await RabbitMQConnectionManager.get_channel()
    queue = await channel.declare_queue('api_aggregation_queue', durable=True)
    reply_queue = await channel.declare_queue('reply_api_aggregation_queue', durable=True)
    consumer_tag = await consume_response(reply_queue, correlation_id, future)
    answer = await get_incomes_in_time_limits_from_db(db, user.get('user_id'),
                                                      date_limits.start_date,
                                                      date_limits.end_date)
    if current not in ('EUR', 'RUB', 'RSD', None):
        raise HTTPException(status_code=400, detail="Currency error: choose only EUR/RUB/RSD or leave this field blank")
    data = {
        'incomes': [item.to_dict() for item in answer],
        'current_currency': current,
        'content': 'Incomes'
    }
    await send_message(channel, json.dumps(data).encode(), queue, reply_queue, correlation_id)

    try:
        response = json.loads(await asyncio.wait_for(future, timeout=10)) #ждем ответа
        #возвращаем ответ юзеру
        return {'incomes': answer} | response
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout") #если ответ не пришел выдаем таймаут
    finally:
        await reply_queue.cancel(consumer_tag) #сворачиваем канал