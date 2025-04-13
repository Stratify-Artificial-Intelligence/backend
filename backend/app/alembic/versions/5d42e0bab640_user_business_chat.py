"""User - Business - Chat

Revision ID: 5d42e0bab640
Revises: 1e7788243394
Create Date: 2025-04-12 18:58:13.888565

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d42e0bab640'
down_revision: Union[str, None] = '1e7788243394'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chats', sa.Column('business_id', sa.Integer(), nullable=False))
    op.drop_constraint('chat_user_id_foreign_key', 'chats', type_='foreignkey')
    op.create_foreign_key(
        'chat_business_id_foreign_key',
        'chats',
        'businesses',
        ['business_id'],
        ['id'],
    )
    op.drop_column('chats', 'user_id')


def downgrade() -> None:
    op.add_column(
        'chats',
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.drop_constraint('chat_business_id_foreign_key', 'chats', type_='foreignkey')
    op.create_foreign_key(
        'chat_user_id_foreign_key',
        'chats',
        'users',
        ['user_id'],
        ['id'],
    )
    op.drop_column('chats', 'business_id')
