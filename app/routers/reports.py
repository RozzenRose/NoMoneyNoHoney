from fastapi import APIRouter
import httpx, io, uuid, asyncio, aio_pika, io, json
from starlette.responses import StreamingResponse
from app.rabbitmq.connection import RabbitMQConnectionManager
from typing import Annotated
from app.schemas import PurchaseTimeLimits
from app.database.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.functions.auth_functions import get_current_user
from app.database.db_functions import (get_purchases_in_limits_from_db,
                                       get_incomes_in_time_limits_from_db,
                                       get_all_categories_from_db)


router = APIRouter(prefix='/reports', tags=['reports'])


@router.get('/rab_ask')
async def get_rab_report(db: Annotated[AsyncSession, Depends(get_db)],
                         user: Annotated[dict, Depends(get_current_user)],
                         date_limits: Annotated[PurchaseTimeLimits, Depends()]):

    purchases = await get_purchases_in_limits_from_db(db, user.get('user_id'),
                                                      date_limits.start_date,
                                                      date_limits.end_date)

    incomes = await get_incomes_in_time_limits_from_db(db, user.get('user_id'),
                                                       date_limits.start_date,
                                                       date_limits.end_date)

    categories = await get_all_categories_from_db(db, user.get('user_id'))

    data = {'purchases': [item.to_dict() for item in purchases],
            'incomes': [item.to_dict() for item in incomes],
            'categories': [item.to_dict() for item in categories]}

    loop = asyncio.get_running_loop()
    future = loop.create_future()
    correlation_id = str(uuid.uuid4())
    channel = await RabbitMQConnectionManager.get_channel()
    queue = await channel.declare_queue('report_queue', durable=False)
    reply_queue = await channel.declare_queue('plot_queue', durable=True)

    async def on_message(message: aio_pika.IncomingMessage) -> None:
        async with message.process():
            if message.correlation_id == correlation_id:
                future.set_result(message.body)

    consumer_tag = await reply_queue.consume(on_message)

    await channel.default_exchange.publish(
        aio_pika.Message(body=json.dumps(data).encode(), reply_to=reply_queue.name,
                         correlation_id=correlation_id),
        routing_key=queue.name)

    try:
        response = await asyncio.wait_for(future, timeout=10)
        print(" [x] Получен ответ")
        return StreamingResponse(io.BytesIO(response), media_type='application/pdf', headers = {
        "Content-Disposition": "attachment; filename=example.pdf"})
    except asyncio.TimeoutError:
        print(" [!] Не дождались ответа")
    finally:
        await reply_queue.cancel(consumer_tag)