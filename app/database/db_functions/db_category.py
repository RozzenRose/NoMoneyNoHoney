from app.database.models import User, Purchase, Income, Category
from sqlalchemy import insert, select, or_
from app.redis import Redis
import json


async def create_category_in_db(db, owner, category_name) -> None:
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
