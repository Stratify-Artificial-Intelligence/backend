"""Chat and chat message

Revision ID: 1e61bc25fac6
Revises: c39919d2d70f
Create Date: 2025-03-05 20:58:44.472270

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e61bc25fac6'
down_revision: Union[str, None] = 'c39919d2d70f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'chats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('internal_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('internal_id'),
    )
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=True),
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            'sender',
            sa.Enum('user', 'ai_model', name='chatmessagesenderenum'),
            nullable=True,
        ),
        sa.Column('content', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ['chat_id'],
            ['chats.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('content'),
    )
    op.create_index(
        op.f('ix_chat_messages_chat_id'),
        'chat_messages',
        ['chat_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_chat_messages_chat_id'), table_name='chat_messages')
    op.drop_table('chat_messages')
    op.drop_table('chats')
    op.execute('DROP TYPE chatmessagesenderenum')
