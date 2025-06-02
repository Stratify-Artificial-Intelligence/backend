"""Plan with payment service price id

Revision ID: fe38dfc382b9
Revises: a988435382ea
Create Date: 2025-06-02 19:05:05.690129

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe38dfc382b9'
down_revision: Union[str, None] = 'a988435382ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'plans',
        sa.Column('payment_service_price_id', sa.String(length=100), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('plans', 'payment_service_price_id')
