from sqlalchemy import insert, select, func, extract
from app.database.models import User, Purchase, Income, Category


async def create_income_in_db(db, owner, discription, quantity, is_rub, is_euro, is_rsd) -> None:
    data = insert(Income).values(
        owner_id=int(owner),
        description=discription,
        quantity=quantity,
        is_rub=is_rub,
        is_euro=is_euro,
        is_rsd=is_rsd)
    await db.execute(data)
    await db.commit()


async def get_all_incomes_from_db(db, user_id) -> list[Income]:
    query = select(Income).where(Income.owner_id==user_id)
    answer = await db.execute(query)
    return answer.scalars().all()


async def get_incomes_current_from_db(db, user_id) -> list[Income]:
    query = (
        select(Income)
        .where(
            Income.owner_id == user_id,
            extract("month", Income.created_at) == extract("month", func.now())
        )
    )
    answer = await db.execute(query)
    return answer.scalars().all()


async def get_incomes_last_month_from_db(db, user_id) -> list[Income]:
    query = (
        select(Income)
        .where(
            Income.owner_id == user_id,
            extract("month", Income.created_at) == extract("month", func.now()) - 1
        )
    )
    answer = await db.execute(query)
    return answer.scalars().all()