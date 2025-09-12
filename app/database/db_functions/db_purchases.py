from app.database.models import User, Purchase, Income, Category
from sqlalchemy import insert


async def create_purchases_list_in_db(db, purchases, owner_id) -> None:
    data = [{**dict(item), 'owner_id': owner_id} for item in purchases.purchases]
    query = insert(Purchase).values(data)
    await db.execute(query)
    await db.commit()
