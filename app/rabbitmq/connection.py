import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractChannel
from typing import Optional
from app.config import settings


class RabbitMQConnectionManager:
    _connection: Optional[AbstractRobustConnection] = None
    _channel: Optional[AbstractChannel] = None
    _url: str = settings.rabbitmq_url


    @classmethod
    async def get_connection(cls) -> AbstractRobustConnection:
        if cls._connection is None or cls._connection.is_closed:
            cls._connection = await aio_pika.connect_robust(cls._url)
        return cls._connection


    @classmethod
    async def get_channel(cls) -> AbstractChannel:
        if cls._channel is None or cls._channel.is_closed:
            connection = await cls.get_connection()
            cls._channel = await connection.channel()
        return cls._channel


    @classmethod
    async def close_connection(cls):
        if cls._channel and not cls._channel.is_closed:
            await cls._channel.close()
        if cls._connection and not cls._connection.is_closed:
            await cls._connection.close()
