import aio_pika, asyncio, uuid, json
from app.rabbitmq import RabbitMQConnectionManager


async def consume_response(reply_queue, correlation_id: str, future: asyncio.Future):
    async def on_message(message: aio_pika.IncomingMessage) -> None:
        async with message.process():
            if message.correlation_id == correlation_id and not future.done():
                future.set_result(message.body)

    consumer_tag = await reply_queue.consume(on_message)
    return consumer_tag


async def send_message(channel, data, queue, reply_queue, correlation_id):
    await channel.default_exchange.publish(
        aio_pika.Message(body=data, reply_to=reply_queue.name,
                         correlation_id=correlation_id),
        routing_key=queue.name)


async def rpc_incomes_request(future, data, current):
    correlation_id = str(uuid.uuid4())  # создаем уникальный id для сообщения
    channel = await RabbitMQConnectionManager.get_channel()
    queue = await channel.declare_queue('api_aggregation_queue', durable=True)
    reply_queue = await channel.declare_queue('reply_api_aggregation_queue', durable=True)
    consumer_tag = await consume_response(reply_queue, correlation_id, future)
    data = {'incomes': [item.to_dict() for item in data], 'current_currency': current, 'content': 'Incomes'}
    await send_message(channel, json.dumps(data).encode(), queue, reply_queue, correlation_id)
    return reply_queue, consumer_tag


async def rpc_puchases_request(future, data, current):
    correlation_id = str(uuid.uuid4())
    channel = await RabbitMQConnectionManager.get_channel()
    queue = await channel.declare_queue('api_aggregation_queue', durable=True)
    reply_queue = await channel.declare_queue('reply_api_aggregation_queue', durable=True)
    consumer_tag = await consume_response(reply_queue, correlation_id, future)
    data = {'purchases': [item.to_dict() for item in data], 'current_currency': current, 'content': 'Purchases'}
    await send_message(channel, json.dumps(data).encode(), queue, reply_queue, correlation_id)
    return reply_queue, consumer_tag


async def rpc_report_request(future, data, current):
    correlation_id = str(uuid.uuid4())
    channel = await RabbitMQConnectionManager.get_channel()
    queue = await channel.declare_queue('report_queue', durable=True)
    reply_queue = await channel.declare_queue('reply_report_queue', durable=True)
    consumer_tag = await consume_response(reply_queue, correlation_id, future)
    await send_message(channel, json.dumps(data).encode(), queue, reply_queue, correlation_id)
    return reply_queue, consumer_tag