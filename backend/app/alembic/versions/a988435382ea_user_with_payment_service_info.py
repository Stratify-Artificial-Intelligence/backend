"""User with payment service info

Revision ID: a988435382ea
Revises: 125f24f8b24b
Create Date: 2025-06-01 17:29:30.439775

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a988435382ea'
down_revision: Union[str, None] = '125f24f8b24b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('plans', sa.Column('price', sa.Float(), nullable=False))
    op.add_column(
        'users',
        sa.Column('payment_service_user_id', sa.String(length=100), nullable=True),
    )
    op.add_column(
        'users',
        sa.Column(
            'payment_service_subscription_id',
            sa.String(length=100),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column('users', 'payment_service_subscription_id')
    op.drop_column('users', 'payment_service_user_id')
    op.drop_column('plans', 'price')
