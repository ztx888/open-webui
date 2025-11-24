"""add model pricing fields

Revision ID: eddd1a9322ad
Revises: d31026856c01
Create Date: 2024-09-05 00:00:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect  # 必须引入这个检查工具

# revision identifiers, used by Alembic.
revision = 'eddd1a9322ad'
down_revision = 'd31026856c01'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- 1. 获取数据库检查员 ---
    bind = op.get_bind()
    inspector = inspect(bind)
    # 获取 'model' 表里现有的所有列名
    existing_columns = [c['name'] for c in inspector.get_columns('model')]

    with op.batch_alter_table('model') as batch_op:
        # --- 2. 逐个检查：只有列不存在时，才添加 ---
        
        if 'input_price_value' not in existing_columns:
            batch_op.add_column(sa.Column('input_price_value', sa.Float(), nullable=True, server_default='0'))
            
        if 'input_price_unit' not in existing_columns:
            batch_op.add_column(sa.Column('input_price_unit', sa.Text(), nullable=True, server_default='M'))
            
        if 'output_price_value' not in existing_columns:
            batch_op.add_column(sa.Column('output_price_value', sa.Float(), nullable=True, server_default='0'))
            
        if 'output_price_unit' not in existing_columns:
            batch_op.add_column(sa.Column('output_price_unit', sa.Text(), nullable=True, server_default='M'))
            
        if 'price_group_multiplier' not in existing_columns:
            batch_op.add_column(sa.Column('price_group_multiplier', sa.Float(), nullable=True, server_default='1.0'))


def downgrade() -> None:
    # 降级时也检查一下再删，防止报错
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = [c['name'] for c in inspector.get_columns('model')]

    with op.batch_alter_table('model') as batch_op:
        if 'price_group_multiplier' in existing_columns:
            batch_op.drop_column('price_group_multiplier')
        if 'output_price_unit' in existing_columns:
            batch_op.drop_column('output_price_unit')
        if 'output_price_value' in existing_columns:
            batch_op.drop_column('output_price_value')
        if 'input_price_unit' in existing_columns:
            batch_op.drop_column('input_price_unit')
        if 'input_price_value' in existing_columns:
            batch_op.drop_column('input_price_value')