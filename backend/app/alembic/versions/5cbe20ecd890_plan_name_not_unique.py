"""Plan name not unique

Revision ID: 5cbe20ecd890
Revises: fe38dfc382b9
Create Date: 2025-06-03 14:07:57.204561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5cbe20ecd890'
down_revision: Union[str, None] = 'fe38dfc382b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('plans_name_key', 'plans', type_='unique')


def downgrade() -> None:
    op.create_unique_constraint('plans_name_key', 'plans', ['name'])
