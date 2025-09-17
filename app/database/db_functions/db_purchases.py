from app.database.models import User, Purchase, Income, Category
from sqlalchemy import insert, select, func
from datetime import timedelta


async def create_purchases_list_in_db(db, purchases, owner_id) -> None:
    data = [{**dict(item), 'owner_id': owner_id} for item in purchases.purchases]
    query = insert(Purchase).values(data)
    await db.execute(query)
    await db.commit()


async def get_all_purchases_from_db(db, owner_id) -> list[Purchase]:
    querry = select(Purchase).where(Purchase.owner_id==owner_id)
    answer = await db.execute(querry)
    return answer.scalars().all()


async def get_purchases_current_week_from_db(db, owner_id) -> list[Purchase]:
    querry = select(Purchase).where(Purchase.owner_id==owner_id,
                                    Purchase.created_at >= func.current_date() - timedelta(days=7))
    answer = await db.execute(querry)
    return answer.scalars().all()

async def get_purchases_in_limits_from_db(db, owner_id, start_date, end_date) -> list[Purchase]:
    query = select(Purchase).where(Purchase.owner_id==owner_id,
                                    Purchase.created_at >= start_date,
                                    Purchase.created_at <= end_date)
    answer = await db.execute(query)
    return answer.scalars().all()
