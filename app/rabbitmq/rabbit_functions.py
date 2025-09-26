import aio_pika, asyncio


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