"""update Category

Revision ID: 44ae1382076a
Revises: fe33e91a67e2
Create Date: 2025-09-11 16:32:44.423805

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '44ae1382076a'
down_revision: Union[str, Sequence[str], None] = 'fe33e91a67e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Добавляем колонку owner_id
    op.add_column('categories', sa.Column('owner_id', sa.Integer(), nullable=True))

    # 2. Создаём внешний ключ на users.id
    op.create_foreign_key(
        'fk_categories_owner_id',  # имя ограничения
        'categories',              # таблица источника
        'users',                   # таблица назначения
        ['owner_id'],              # локальная колонка
        ['id']                     # колонка в users
    )

    # 3. Добавляем колонку is_root
    op.add_column('categories', sa.Column('is_root', sa.Boolean(), server_default=sa.false(), nullable=False))

    # 4. Удаляем колонку parent_id_category
    op.drop_column('categories', 'parent_id_category')


def downgrade():
    # 1. Восстанавливаем parent_id_category
    op.add_column('categories', sa.Column('parent_id_category', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_categories_parent_id_category',
        'categories',
        'categories',
        ['parent_id_category'],
        ['id']
    )

    # 2. Удаляем колонку is_root
    op.drop_column('categories', 'is_root')

    # 3. Удаляем внешний ключ owner_id
    op.drop_constraint('fk_categories_owner_id', 'categories', type_='foreignkey')

    # 4. Удаляем колонку owner_id
    op.drop_column('categories', 'owner_id')