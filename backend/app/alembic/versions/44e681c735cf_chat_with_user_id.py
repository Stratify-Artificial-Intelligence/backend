"""Chat with user id

Revision ID: 44e681c735cf
Revises: 96ac1945e322
Create Date: 2025-03-24 20:37:14.013652

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44e681c735cf'
down_revision: Union[str, None] = '96ac1945e322'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chats', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(
        'chat_user_id_foreign_key',
        'chats',
        'users',
        ['user_id'],
        ['id'],
    )


def downgrade() -> None:
    op.drop_constraint('chat_user_id_foreign_key', 'chats', type_='foreignkey')
    op.drop_column('chats', 'user_id')
