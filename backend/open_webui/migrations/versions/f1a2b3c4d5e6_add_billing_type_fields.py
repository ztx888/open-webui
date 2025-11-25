"""add billing type fields

Revision ID: f1a2b3c4d5e6
Revises: 92715d6d9265
Create Date: 2025-11-25 14:00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# 【关键】这里填新脚本的 ID
revision = 'f1a2b3c4d5e6'
# 【关键】这里填你刚才确认过的上一个合并节点的 ID
down_revision = '92715d6d9265'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- 1. 获取数据库检查员 ---
    bind = op.get_bind()
    inspector = inspect(bind)
    # 获取 'model' 表中的现有列
    existing_columns = [c['name'] for c in inspector.get_columns('model')]

    with op.batch_alter_table('model') as batch_op:
        # --- 2. 添加字段：只在列不存在时添加 (防呆设计) ---
        
        if 'billing_type' not in existing_columns:
            # 默认值为 'per_token' (按量计费)
            batch_op.add_column(sa.Column('billing_type', sa.Text(), nullable=True, server_default='per_token'))
            
        if 'per_request_price' not in existing_columns:
            # 默认价格为 0
            batch_op.add_column(sa.Column('per_request_price', sa.Float(), nullable=True, server_default='0'))


def downgrade() -> None:
    # 降级时也检查一下
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = [c['name'] for c in inspector.get_columns('model')]

    with op.batch_alter_table('model') as batch_op:
        if 'per_request_price' in existing_columns:
            batch_op.drop_column('per_request_price')
        if 'billing_type' in existing_columns:
            batch_op.drop_column('billing_type')