"""User role: Service user

Revision ID: 9be920aea925
Revises: 670c77d8dd27
Create Date: 2025-08-02 18:10:36.088451

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9be920aea925'
down_revision: Union[str, None] = '670c77d8dd27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute('ALTER TYPE userroleenum RENAME TO userroleenum_old')

    new_user_role_enum = sa.Enum('Admin', 'Basic', 'Service', name='userroleenum')
    new_user_role_enum.create(op.get_bind(), checkfirst=False)

    op.alter_column(
        'users',
        'role',
        type_=new_user_role_enum,
        existing_type=sa.Enum('Admin', 'Basic', name='userroleenum_old'),
        existing_nullable=True,
        postgresql_using='role::text::userroleenum',
    )

    op.execute('DROP TYPE userroleenum_old')


def downgrade():
    op.execute('ALTER TYPE userroleenum RENAME TO userroleenum_new')

    old_user_role_enum = sa.Enum('Admin', 'Basic', name='userroleenum')
    old_user_role_enum.create(op.get_bind(), checkfirst=False)

    op.alter_column(
        'users',
        'role',
        type_=old_user_role_enum,
        existing_type=sa.Enum('Admin', 'Basic', 'Premium', name='userroleenum_new'),
        existing_nullable=True,
        postgresql_using='role::text::userroleenum',
    )

    op.execute('DROP TYPE userroleenum_new')
