from app.database.models import User, Purchase, Income, Category
from sqlalchemy import insert, select, or_, delete
from app.redis import Redis
import json


async def create_category_in_db(db, owner, category_name) -> None:
    '''Создание категорий сносит весь кеш категорий юзера'''
    redis = await Redis.get_redis()
    pattern = f'{owner}: categories*'
    async for key in redis.scan_iter(pattern):
        await redis.unlink(key)
    data = insert(Category).values(
        owner_id=int(owner),
        category_name=category_name)
    await db.execute(data)
    await db.commit()


async def get_all_categories_from_db(db, user_id) -> list[Category]:
    redis = await Redis.get_redis()
    cache_key = f'{user_id}: categories'
    cache = await redis.get(cache_key)
    if cache:
        data = json.loads(cache)
        return [Category.from_json(item) for item in data]
    query = select(Category).where(or_(Category.owner_id == user_id,
                                       Category.is_root.is_(True)))
    answer = await db.execute(query)
    data = answer.scalars().all()
    await redis.set(cache_key, json.dumps([item.to_dict() for item in data]), ex=180)
    return data


async def delete_categories_from_db(db, owner_id, categories_id):
    '''Удаление сносит весь кеш категорий юзера'''
    redis = await Redis.get_redis()
    pattern = f'{owner_id}: categories*'
    async for key in redis.scan_iter(pattern):
        await redis.unlink(key)
    query = delete(Category).where(Category.owner_id == owner_id,
                                 Category.id.in_(categories_id))
    await db.execute(query)
    await db.commit()

