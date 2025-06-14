"""User with external id and not password

Revision ID: 290d0b7eabbd
Revises: 5cbe20ecd890
Create Date: 2025-06-13 18:12:48.564827

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '290d0b7eabbd'
down_revision: Union[str, None] = '5cbe20ecd890'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('external_id', sa.String(length=50), nullable=True))
    op.alter_column(
        'users',
        'email',
        existing_type=sa.VARCHAR(length=50),
        nullable=False,
    )
    op.create_unique_constraint('users_email_unique', 'users', ['email'])
    op.create_unique_constraint('users_external_id_unique', 'users', ['external_id'])
    op.drop_column('users', 'hashed_password')


def downgrade() -> None:
    op.add_column(
        'users',
        sa.Column(
            'hashed_password',
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_constraint('users_email_unique', 'users', type_='unique')
    op.drop_constraint('users_external_id_unique', 'users', type_='unique')
    op.alter_column('users', 'email', existing_type=sa.VARCHAR(length=50), nullable=True)
    op.drop_column('users', 'external_id')
