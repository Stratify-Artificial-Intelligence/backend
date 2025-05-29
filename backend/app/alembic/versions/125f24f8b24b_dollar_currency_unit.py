"""Dollar currency unit

Revision ID: 125f24f8b24b
Revises: 3656a015dcf8
Create Date: 2025-05-29 16:48:03.960616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '125f24f8b24b'
down_revision: Union[str, None] = '3656a015dcf8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE currencyunitenum ADD VALUE IF NOT EXISTS 'dollar'")


def downgrade() -> None:
    pass
