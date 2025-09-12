from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from app.database.db_depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import CreateIncome, IncomeTimeLimits
from app.database.db_functions import (create_income_in_db, get_all_incomes_from_db,
                                       get_incomes_current_from_db, get_incomes_last_month_from_db,
                                       get_incomes_in_time_limits_from_db)
from app.functions.auth_functions import get_current_user


router = APIRouter(prefix='/incomes', tags=['incomes'])


@router.post('/new_income', status_code=status.HTTP_201_CREATED)
async def create_income(db: Annotated[AsyncSession, Depends(get_db)],
                        income: CreateIncome,
                        user: Annotated[dict, Depends(get_current_user)]):
    await create_income_in_db(db, user.get('user_id'), income.description, income.quantity,
                              income.is_rub, income.is_euro, income.is_rsd)
    return {'status_code':status.HTTP_201_CREATED,
            'transaction': 'Income created successfully'}


@router.get('/all_your_incomes')
async def get_all_incomes(db: Annotated[AsyncSession, Depends(get_db)],
                          user: Annotated[dict, Depends(get_current_user)]):
    answer = await get_all_incomes_from_db(db, user.get('user_id'))
    return {'incomes': answer}


@router.get('/incomes_current_month')
async def get_incomes_current_month(db: Annotated[AsyncSession, Depends(get_db)],
                                    user: Annotated[dict, Depends(get_current_user)]):
    answer = await get_incomes_current_from_db(db, user.get('user_id'))
    return {'incomes': answer}


@router.get('/incomes_last_month')
async def get_incomes_last_month(db: Annotated[AsyncSession, Depends(get_db)],
                                 user: Annotated[dict, Depends(get_current_user)]):
    answer = await get_incomes_last_month_from_db(db, user.get('user_id'))
    return {'incomes': answer}


@router.get('/incomes_limits')
async def get_incomes_in_time_limits(db: Annotated[AsyncSession, Depends(get_db)],
                                     user: Annotated[dict, Depends(get_current_user)],
                                     date_limits: IncomeTimeLimits = Depends()):
    answer = await get_incomes_in_time_limits_from_db(db, user.get('user_id'),
                                                      date_limits.start_date,
                                                      date_limits.end_date)
    return {'incomes': answer}