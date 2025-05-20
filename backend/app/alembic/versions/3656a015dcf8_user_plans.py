"""User plans

Revision ID: 3656a015dcf8
Revises: 4f806464bfec
Create Date: 2025-05-20 19:48:06.019514

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3656a015dcf8'
down_revision: Union[str, None] = '4f806464bfec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column(
            'name',
            sa.Enum('Starter', 'Founder', 'CEO', name='userplanenum'),
            nullable=False,
        ),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.add_column('users', sa.Column('plan_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_user_plan', 'users', 'plans', ['plan_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_user_plan', 'users', type_='foreignkey')
    op.drop_column('users', 'plan_id')
    op.drop_table('plans')
    op.execute('DROP TYPE userplanenum')
