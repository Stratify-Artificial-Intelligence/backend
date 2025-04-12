"""Business

Revision ID: 1e7788243394
Revises: bd4f4176e38c
Create Date: 2025-04-10 18:15:49.771781

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e7788243394'
down_revision: Union[str, None] = 'bd4f4176e38c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'businesses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('goal', sa.String(), nullable=True),
        sa.Column(
            'stage',
            sa.Enum('idea', 'established', name='businessstageenum'),
            nullable=True,
        ),
        sa.Column('team_size', sa.Integer(), nullable=True),
        sa.Column('team_description', sa.String(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'business_ideas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('competitor_existence', sa.Boolean(), nullable=True),
        sa.Column('competitor_differentiation', sa.String(), nullable=True),
        sa.Column('investment', sa.Float(), nullable=True),
        sa.Column(
            'investment_currency',
            sa.Enum('euro', name='currencyunitenum'),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ['id'],
            ['businesses.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'established_businesses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('billing', sa.Float(), nullable=True),
        sa.Column(
            'billing_currency', sa.Enum('euro', name='currencyunitenum'), nullable=True
        ),
        sa.Column('ebitda', sa.Float(), nullable=True),
        sa.Column(
            'ebitda_currency', sa.Enum('euro', name='currencyunitenum'), nullable=True
        ),
        sa.Column('profit_margin', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ['id'],
            ['businesses.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('established_businesses')
    op.drop_table('business_ideas')
    op.drop_table('businesses')
    op.execute('DROP TYPE currencyunitenum')
    op.execute('DROP TYPE businessstageenum')
