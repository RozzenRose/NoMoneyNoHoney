import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel
from typing import Optional
from app.config import settings


class RabbitMQConnectionManager:
    _connection: Optional[AbstractRobustConnection] = None
    _channels: Optional[AbstractRobustChannel] = {}
    _url: str = settings.rabbitmq_url


    @classmethod
    async def get_connection(cls) -> AbstractRobustConnection:
        if cls._connection is None or cls._connection.is_closed:
            cls._connection = await aio_pika.connect_robust(cls._url)
        return cls._connection


    @classmethod
    async def get_channel(cls, name: str = "default") -> AbstractRobustChannel:
        if name not in cls._channels or cls._channels[name].is_closed:
            connection = await cls.get_connection()
            cls._channels[name] = await connection.channel()
        return cls._channels[name]


    @classmethod
    async def close_all(cls):
        """Закрывает все каналы и соединение"""
        for name, channel in cls._channels.items():
            if channel and not channel.is_closed:
                await channel.close()
        cls._channels.clear()

        if cls._connection and not cls._connection.is_closed:
            await cls._connection.close()
