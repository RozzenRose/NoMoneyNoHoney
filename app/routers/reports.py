from fastapi import APIRouter, Depends, HTTPException
import uuid, asyncio, io, json
from starlette.responses import StreamingResponse
from app.rabbitmq import RabbitMQConnectionManager, consume_response, send_message
from typing import Annotated
from app.schemas import PurchaseTimeLimits
from app.database.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.functions.auth_functions import get_current_user
from app.database.db_functions import (get_purchases_in_limits_from_db,
                                       get_incomes_in_time_limits_from_db,
                                       get_all_categories_from_db)


router = APIRouter(prefix='/reports', tags=['reports'])


@router.get('/report_ask')
async def get_rab_report(db: Annotated[AsyncSession, Depends(get_db)],
                         user: Annotated[dict, Depends(get_current_user)],
                         date_limits: Annotated[PurchaseTimeLimits, Depends()]):
    #достаем данные из бд
    purchases = await get_purchases_in_limits_from_db(db, user.get('user_id'),
                                                      date_limits.start_date,
                                                      date_limits.end_date)
    incomes = await get_incomes_in_time_limits_from_db(db, user.get('user_id'),
                                                       date_limits.start_date,
                                                       date_limits.end_date)
    categories = await get_all_categories_from_db(db, user.get('user_id'))
    #собираем данные в один dict для отправки
    data = {'purchases': [item.to_dict() for item in purchases],
            'incomes': [item.to_dict() for item in incomes],
            'categories': [item.to_dict() for item in categories]}

    loop = asyncio.get_running_loop()
    future = loop.create_future()
    correlation_id = str(uuid.uuid4()) #создаем уникальный id для сообщения
    channel = await RabbitMQConnectionManager.get_channel()
    queue = await channel.declare_queue('report_queue', durable=False)
    reply_queue = await channel.declare_queue('plot_queue', durable=True)
    #подписываемся на ответ
    consumer_tag = await consume_response(reply_queue, correlation_id, future)
    #отправляем сообщение
    await send_message(channel, json.dumps(data).encode(), queue, reply_queue, correlation_id)

    try:
        response = await asyncio.wait_for(future, timeout=10) #ждем ответа
        #возвращаем ответ юзеру
        return StreamingResponse(io.BytesIO(response), media_type='application/pdf', headers = {
        "Content-Disposition": "attachment; filename=example.pdf"})
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout") #если ответ не пришел выдаем таймаут
    finally:
        await reply_queue.cancel(consumer_tag) #сворачиваем канал
