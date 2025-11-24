"""merge_custom_and_official

Revision ID: 92715d6d9265
Revises: 37f288994c47, eddd1a9322ad
Create Date: 2025-11-25 02:34:52.704404

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


# revision identifiers, used by Alembic.
revision: str = '92715d6d9265'
down_revision: Union[str, None] = ('37f288994c47', 'eddd1a9322ad')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
