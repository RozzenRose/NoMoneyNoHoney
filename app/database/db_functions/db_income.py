from sqlalchemy import insert, select, func, extract
from app.database.models import User, Purchase, Income, Category
from app.redis import Redis
import json


async def create_income_in_db(db, owner, discription, quantity, currency) -> None:
    data = insert(Income).values(
        owner_id=int(owner),
        description=discription,
        quantity=quantity,
        currency=currency)
    await db.execute(data)
    await db.commit()


async def get_all_incomes_from_db(db, user_id) -> list[Income]:
    redis = await Redis.get_redis()
    cache_key = f'{user_id}: incomes: all'
    cache = await redis.get(cache_key)
    if cache:
        data = json.loads(cache)
        return [Income.from_json(item) for item in data]
    query = select(Income).where(Income.owner_id==user_id)
    answer = await db.execute(query)
    data = answer.scalars().all()
    await redis.set(cache_key, json.dumps([item.to_dict() for item in data]), ex=180)
    return data


async def get_incomes_current_from_db(db, user_id) -> list[Income]:
    redis = await Redis.get_redis()
    cache_key = f'{user_id}: incomes: current'
    cache = await redis.get(cache_key)
    if cache:
        data = json.loads(cache)
        return [Income.from_json(item) for item in data]
    query = (
        select(Income)
        .where(
            Income.owner_id == user_id,
            extract("month", Income.created_at) == extract("month", func.current_date())
        )
    )
    answer = await db.execute(query)
    data = answer.scalars().all()
    await redis.set(cache_key, json.dumps([item.to_dict() for item in data]), ex=180)
    return data


async def get_incomes_last_month_from_db(db, user_id) -> list[Income]:
    redis = await Redis.get_redis()
    cache_key = f'{user_id}: incomes: last month'
    cache = await redis.get(cache_key)
    if cache:
        data = json.loads(cache)
        return [Income.from_json(item) for item in data]
    query = (
        select(Income)
        .where(
            Income.owner_id == user_id,
            extract("month", Income.created_at) == extract("month", func.current_date()) - 1
        )
    )
    answer = await db.execute(query)
    data = answer.scalars().all()
    await redis.set(cache_key, json.dumps([item.to_dict() for item in data]), ex=180)
    return data


async def get_incomes_in_time_limits_from_db(db, user_id, start_date, end_date) -> list[Income]:
    redis = await Redis.get_redis()
    cache_key = f'{user_id}: incomes: {start_date}-{end_date}'
    cache = await redis.get(cache_key)
    if cache:
        data = json.loads(cache)
        return [Income.from_json(item) for item in data]
    query = (select(Income).where(Income.owner_id == user_id,
                                  Income.created_at >= start_date,
                                  Income.created_at <= end_date))
    answer = await db.execute(query)
    data = answer.scalars().all()
    await redis.set(cache_key, json.dumps([item.to_dict() for item in data]), ex=180)
    return data
