"""User with language

Revision ID: 5c8dbd2b8239
Revises: 87713c25361f
Create Date: 2025-08-24 14:43:20.753514

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c8dbd2b8239'
down_revision: Union[str, None] = '87713c25361f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_language_enum = sa.Enum('es', name='userlanguageenum')
    user_language_enum.create(op.get_bind())

    op.add_column(
        'users',
        sa.Column('language', user_language_enum, nullable=False, server_default='es'),
    )


def downgrade() -> None:
    op.drop_column('users', 'language')
    sa.Enum('es', name='userlanguageenum').drop(op.get_bind())
