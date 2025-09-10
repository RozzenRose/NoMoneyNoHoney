from datetime import datetime, timedelta, timezone
import jwt
from app.config import settings
from fastapi import Depends
from typing import Annotated


async def create_access_token(user_id: int, username: str, email: str, is_admin: bool, expires_delta: timedelta):
    payload = {'user_id': user_id,
               'username': username,
               'email': email,
               'is_admin': is_admin,
               'exp': datetime.now(timezone.utc) + expires_delta}
    payload['exp'] = int(payload['exp'].timestamp())
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)   #Создание токена


async def get_current_user(token):
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm]) #Декодирование токена
    user_id: int | None = payload.get('user_id')
    username: str | None = payload.get('username')
    email: str | None = payload.get('email')
    is_admin: bool | None = payload.get('is_admin')
    expire: int | None = payload.get('exp')

    current_time = datetime.now(timezone.utc).timestamp()

    return {'user_id': user_id,
            'username': username,
            'email': email,
            'is_admin': is_admin,
            'expire': expire > current_time}

