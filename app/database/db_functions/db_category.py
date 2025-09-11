from app.database.models import User, Purchase, Income, Category
from app.schemas import CreateUser
from sqlalchemy import insert, select

async def create_category_in_db(db, owner_id: int, category_name: str) -> None:
    data = insert(Category).values(
        owner_id=owner_id,
        category_name=category_name)
    await db.execute(data)
    await db.commit()
