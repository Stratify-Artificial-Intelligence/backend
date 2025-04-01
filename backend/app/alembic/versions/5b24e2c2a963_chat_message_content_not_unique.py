"""Chat message content not unique

Revision ID: 5b24e2c2a963
Revises: 1e61bc25fac6
Create Date: 2025-03-11 19:49:10.622456

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '5b24e2c2a963'
down_revision: Union[str, None] = '1e61bc25fac6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        'chat_messages_content_key',
        'chat_messages',
        type_='unique',
    )


def downgrade() -> None:
    op.create_unique_constraint(
        'chat_messages_content_key',
        'chat_messages',
        ['content'],
    )
