from app.database.models import User, Purchase, Income, Category
from sqlalchemy import insert, select


async def create_category_in_db(db, owner, category_name) -> None:
    data = insert(Category).values(
        owner_id=int(owner),
        category_name=category_name)
    await db.execute(data)
    await db.commit()


async def get_all_categories_from_db(db, user_id) -> list[Category]:
    query = select(Category).where(Category.owner_id==user_id or Category.is_root==True)
    answer = await db.execute(query)
    return [item.category_name for item in answer.scalars().all()]
