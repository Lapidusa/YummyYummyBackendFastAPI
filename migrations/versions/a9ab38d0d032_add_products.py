"""add products

Revision ID: a9ab38d0d032
Revises: e6dc97b0d0f3
Create Date: 2025-05-13 13:48:42.092227

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a9ab38d0d032'
down_revision: Union[str, None] = 'e6dc97b0d0f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('products',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('type', postgresql.ENUM('GROUP', 'CONSTRUCTOR', 'PIZZA', name='type'), nullable=False),
    sa.Column('is_available', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('replacement_groups',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('max_choices', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pizzas',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('dough', postgresql.ENUM('THICK_DOUGH', 'THIN_DOUGH', name='dough'), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_replacements',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('product_id', sa.UUID(), nullable=True),
    sa.Column('group_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['replacement_groups.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_variants',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('product_id', sa.UUID(), nullable=True),
    sa.Column('size', sa.String(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.Column('calories', sa.Float(), nullable=True),
    sa.Column('proteins', sa.Float(), nullable=True),
    sa.Column('fats', sa.Float(), nullable=True),
    sa.Column('carbohydrates', sa.Float(), nullable=True),
    sa.Column('is_available', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('replacement_items',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('group_id', sa.UUID(), nullable=True),
    sa.Column('product_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['replacement_groups.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('replacement_items')
    op.drop_table('product_variants')
    op.drop_table('product_replacements')
    op.drop_table('pizzas')
    op.drop_table('replacement_groups')
    op.drop_table('products')
    # ### end Alembic commands ###
