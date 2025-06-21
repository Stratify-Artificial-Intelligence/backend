"""Business with logo url

Revision ID: 213a1fd53e8a
Revises: 290d0b7eabbd
Create Date: 2025-06-21 06:36:10.840384

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '213a1fd53e8a'
down_revision: Union[str, None] = '290d0b7eabbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('businesses', sa.Column('logo_url', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('businesses', 'logo_url')
