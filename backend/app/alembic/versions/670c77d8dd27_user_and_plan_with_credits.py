"""User and plan with credits

Revision ID: 670c77d8dd27
Revises: 213a1fd53e8a
Create Date: 2025-07-12 18:04:32.031096

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '670c77d8dd27'
down_revision: Union[str, None] = '213a1fd53e8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('plans', sa.Column('monthly_credits', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('available_credits', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'available_credits')
    op.drop_column('plans', 'monthly_credits')
