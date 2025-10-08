from fastapi import APIRouter, Depends, HTTPException
import uuid, asyncio, io, json
from starlette.responses import StreamingResponse
from app.rabbitmq import rpc_report_request
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
                         date_limits: Annotated[PurchaseTimeLimits, Depends()],
                         current: str | None = 'EUR'):
    if current not in ('EUR', 'RUB', 'RSD', None):
        raise HTTPException(status_code=400, detail="Currency error: choose only EUR/RUB/RSD or leave this field blank")

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
            'categories': [item.to_dict() for item in categories],
            'current_currency': current}

    future = asyncio.get_running_loop().create_future() # гтовим футура для ответа
    reply_queue, consumer_tag = await rpc_report_request(future, data, current) # отправляем данные

    try:
        response = await asyncio.wait_for(future, timeout=10) #ждем ответа
        #возвращаем ответ юзеру
        return StreamingResponse(io.BytesIO(response), media_type='application/pdf', headers = {
        "Content-Disposition": "attachment; filename=example.pdf"})
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timeout") #если ответ не пришел выдаем таймаут
    finally:
        await reply_queue.cancel(consumer_tag) #сворачиваем канал
