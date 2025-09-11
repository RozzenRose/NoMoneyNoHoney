from app.database.models import User, Purchase, Income, Category
from app.schemas import CreateCategory
from sqlalchemy import insert


async def create_category_in_db(db, create_category: CreateCategory) -> None:
    data = insert(Category).values(
        owner_id=create_category.owner_id,
        category_name=create_category.category_name)
    await db.execute(data)
    await db.commit()
