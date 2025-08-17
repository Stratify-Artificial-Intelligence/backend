"""User without payment_service_subscription_id

Revision ID: 87713c25361f
Revises: 9be920aea925
Create Date: 2025-08-17 17:40:58.593201

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87713c25361f'
down_revision: Union[str, None] = '9be920aea925'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('users', 'payment_service_subscription_id')


def downgrade() -> None:
    op.add_column(
        'users',
        sa.Column(
            'payment_service_subscription_id',
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=True,
        ),
    )
