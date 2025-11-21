"""add model pricing fields

Revision ID: eddd1a9322ad
Revises: d31026856c01
Create Date: 2024-09-05 00:00:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'eddd1a9322ad'
down_revision = 'd31026856c01'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('model') as batch_op:
        batch_op.add_column(sa.Column('input_price_value', sa.Float(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('input_price_unit', sa.Text(), nullable=True, server_default='M'))
        batch_op.add_column(sa.Column('output_price_value', sa.Float(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('output_price_unit', sa.Text(), nullable=True, server_default='M'))
        batch_op.add_column(sa.Column('price_group_multiplier', sa.Float(), nullable=True, server_default='1.0'))


def downgrade() -> None:
    with op.batch_alter_table('model') as batch_op:
        batch_op.drop_column('price_group_multiplier')
        batch_op.drop_column('output_price_unit')
        batch_op.drop_column('output_price_value')
        batch_op.drop_column('input_price_unit')
        batch_op.drop_column('input_price_value')
