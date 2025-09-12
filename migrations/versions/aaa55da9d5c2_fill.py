"""fill

Revision ID: aaa55da9d5c2
Revises: dd766e9da6a3
Create Date: 2025-09-12 17:16:47.103210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aaa55da9d5c2'
down_revision: Union[str, Sequence[str], None] = 'dd766e9da6a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Insert default categories directly into the categories table
    op.execute("""
        INSERT INTO categories (category_name, is_root)
        VALUES 
            ('Food', true),
            ('Transport', true),
            ('Entertainment', true),
            ('Shopping', true),
            ('Clothing', true),
            ('Health', true),
            ('Housing', true),
            ('Other', true)
    """)


def downgrade() -> None:
    # Delete the default categories by name
    op.execute("""
        DELETE FROM categories 
        WHERE category_name IN ('Food', 'Transport', 'Entertainment', 'Shopping', 'Clothing', 'Health', 'Housing', 'Other')
        AND is_root = true
    """)