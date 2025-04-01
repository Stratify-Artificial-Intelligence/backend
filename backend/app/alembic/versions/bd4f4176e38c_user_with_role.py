"""User with role

Revision ID: bd4f4176e38c
Revises: 44e681c735cf
Create Date: 2025-03-26 07:35:07.473153

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd4f4176e38c'
down_revision: Union[str, None] = '44e681c735cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role_enum = sa.Enum('Admin', 'Basic', name='userroleenum')
    user_role_enum.create(op.get_bind())

    op.add_column(
        'users',
        sa.Column('role', user_role_enum, nullable=False),
    )


def downgrade() -> None:
    op.drop_column('users', 'role')
    sa.Enum('Admin', 'Basic', name='userroleenum').drop(op.get_bind())
