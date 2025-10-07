from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from app.database.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.functions.auth_functions import get_current_user
from app.schemas import PurchasesListCreate, PurchaseTimeLimits
from app.database.db_functions import (create_purchases_list_in_db, get_all_purchases_from_db,
                                get_purchases_current_week_from_db, get_purchases_in_limits_from_db)
from app.rabbitmq import RabbitMQConnectionManager, consume_response, send_message
import asyncio, uuid, json


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
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    correlation_id = str(uuid.uuid4())
    channel = await RabbitMQConnectionManager.get_channel()
    queue = await channel.declare_queue('api_aggregation_queue', durable=True)
    reply_queue = await channel.declare_queue('reply_api_aggregation_queue', durable=True)
    consumer_tag = await consume_response(reply_queue, correlation_id, future)
    answer = await get_all_purchases_from_db(db, user.get('user_id'))
    if current not in ('EUR', 'RUB', 'RSD', None):
        raise HTTPException(status_code=400, detail="Currency error: choose only EUR/RUB/RSD or leave this field blank")
    data = {'purchases': [item.to_dict() for item in answer], 'current_currency': current, 'content': 'Purchases'}
    await send_message(channel, json.dumps(data).encode(), queue, reply_queue, correlation_id)

    try:
        response = json.loads(await asyncio.wait_for(future, timeout=10))
        return {'purchases': answer} | response
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout")
    finally:
        await reply_queue.cancel(consumer_tag)


@router.get('/last_7_days_purchases')
async def get_last_7_days_purchases(db: Annotated[AsyncSession, Depends(get_db)],
                                     user: Annotated[dict, Depends(get_current_user)],
                                     current: str | None = None):
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    correlation_id = str(uuid.uuid4())
    channel = await RabbitMQConnectionManager.get_channel()
    queue = await channel.declare_queue('api_aggregation_queue', durable=True)
    reply_queue = await channel.declare_queue('reply_api_aggregation_queue', durable=True)
    consumer_tag = await consume_response(reply_queue, correlation_id, future)
    answer = await get_purchases_current_week_from_db(db, user.get('user_id'))
    if current not in ('EUR', 'RUB', 'RSD', None):
        raise HTTPException(status_code=400, detail="Currency error: choose only EUR/RUB/RSD or leave this field blank")
    data = {'purchases': [item.to_dict() for item in answer], 'current_currency': current, 'content': 'Purchases'}
    await send_message(channel, json.dumps(data).encode(), queue, reply_queue, correlation_id)

    try:
        response = json.loads(await asyncio.wait_for(future, timeout=10))
        return {'purchases': answer} | response
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout")
    finally:
        await reply_queue.cancel(consumer_tag)


@router.get('/purchases_limits')
async def get_purchases_in_limits(db: Annotated[AsyncSession, Depends(get_db)],
                                  user: Annotated[dict, Depends(get_current_user)],
                                  date_limits: Annotated[PurchaseTimeLimits, Depends()],
                                  current: str | None = None):
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    correlation_id = str(uuid.uuid4())
    channel = await RabbitMQConnectionManager.get_channel()
    queue = await channel.declare_queue('api_aggregation_queue', durable=True)
    reply_queue = await channel.declare_queue('reply_api_aggregation_queue', durable=True)
    consumer_tag = await consume_response(reply_queue, correlation_id, future)
    answer = await get_purchases_in_limits_from_db(db, user.get('user_id'),
                                                  date_limits.start_date,
                                                  date_limits.end_date)
    if current not in ('EUR', 'RUB', 'RSD', None):
        raise HTTPException(status_code=400, detail="Currency error: choose only EUR/RUB/RSD or leave this field blank")
    data = {'purchases': [item.to_dict() for item in answer], 'current_currency': current, 'content': 'Purchases'}
    await send_message(channel, json.dumps(data).encode(), queue, reply_queue, correlation_id)

    try:
        response = json.loads(await asyncio.wait_for(future, timeout=10))
        return {'purchases': answer} | response
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout")
    finally:
        await reply_queue.cancel(consumer_tag)
