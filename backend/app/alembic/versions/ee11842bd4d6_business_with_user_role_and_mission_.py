"""Business with user role and mission/vision

Revision ID: ee11842bd4d6
Revises: 5d42e0bab640
Create Date: 2025-04-14 06:32:31.452432

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee11842bd4d6'
down_revision: Union[str, None] = '5d42e0bab640'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('businesses', sa.Column('user_position', sa.String(), nullable=True))
    op.add_column(
        'established_businesses',
        sa.Column('mission_and_vision', sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('established_businesses', 'mission_and_vision')
    op.drop_column('businesses', 'user_position')
