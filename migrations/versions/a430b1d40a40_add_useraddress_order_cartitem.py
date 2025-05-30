"""add UserAddress Order CartItem

Revision ID: a430b1d40a40
Revises: c068298c876d
Create Date: 2025-05-27 18:48:11.945216

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a430b1d40a40'
down_revision: Union[str, None] = 'c068298c876d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('orders',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('total_price', sa.Float(), nullable=False),
    sa.Column('is_pickup', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('status', postgresql.ENUM('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='orderstatus'), nullable=False),
    sa.Column('payment_method', sa.Enum('CASH', 'ELECTRONIC', name='payment_method_enum'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_addresses',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('street', sa.String(), nullable=False),
    sa.Column('house', sa.String(), nullable=False),
    sa.Column('apartment', sa.String(), nullable=True),
    sa.Column('label', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order_addresses',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('order_id', sa.UUID(), nullable=False),
    sa.Column('street', sa.String(), nullable=False),
    sa.Column('house', sa.String(), nullable=False),
    sa.Column('apartment', sa.String(), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cart_items',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('product_variant_id', sa.UUID(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('added_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['product_variant_id'], ['product_variants.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order_items',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('order_id', sa.UUID(), nullable=False),
    sa.Column('product_variant_id', sa.UUID(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('price_per_item', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['product_variant_id'], ['product_variants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('us_gaz',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('seq', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('word', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('stdword', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('token', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('is_custom', sa.BOOLEAN(), server_default=sa.text('true'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_us_gaz')
    )
    op.create_table('us_lex',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('seq', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('word', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('stdword', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('token', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('is_custom', sa.BOOLEAN(), server_default=sa.text('true'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_us_lex')
    )
    op.create_table('us_rules',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('rule', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('is_custom', sa.BOOLEAN(), server_default=sa.text('true'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_us_rules')
    )
    op.create_table('pointcloud_formats',
    sa.Column('pcid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('schema', sa.TEXT(), autoincrement=False, nullable=True),
    sa.CheckConstraint('pc_schemaisvalid(schema)', name='pointcloud_formats_schema_check'),
    sa.CheckConstraint('pcid > 0 AND pcid < 65536', name='pointcloud_formats_pcid_check'),
    sa.PrimaryKeyConstraint('pcid', name='pointcloud_formats_pkey')
    )
    op.drop_table('order_items')
    op.drop_table('cart_items')
    op.drop_table('order_addresses')
    op.drop_table('user_addresses')
    op.drop_table('orders')
    # ### end Alembic commands ###
