from fastapi import APIRouter
import httpx, io, uuid, asyncio
from starlette.responses import StreamingResponse
from app.rabbitmq.connection import RabbitMQConnectionManager
import aio_pika


router = APIRouter(prefix='/reports', tags=['reports'])


@router.get('/ask')
async def get_report():
    async with httpx.AsyncClient() as client:
        report = await client.get('http://127.0.0.1:8001/reports/ask')
        report.raise_for_status()
        buf = io.BytesIO(report.content)
        return StreamingResponse(buf, media_type='image/png')


@router.get('/rab_ask')
async def get_rab_report():
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
        aio_pika.Message(body=b'Hello, RabbitMQ!', reply_to=reply_queue.name,
                         correlation_id=correlation_id),
        routing_key=queue.name)

    try:
        response = await asyncio.wait_for(future, timeout=10)
        print(" [x] Получен ответ:", response.decode())
    except asyncio.TimeoutError:
        print(" [!] Не дождались ответа")
    finally:
        await reply_queue.cancel(consumer_tag)