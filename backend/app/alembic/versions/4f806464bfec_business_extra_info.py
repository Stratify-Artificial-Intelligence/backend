"""Business extra info

Revision ID: 4f806464bfec
Revises: ee11842bd4d6
Create Date: 2025-05-17 09:26:17.668153

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f806464bfec'
down_revision: Union[str, None] = 'ee11842bd4d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('businesses', sa.Column('extra_info', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('businesses', 'extra_info')
