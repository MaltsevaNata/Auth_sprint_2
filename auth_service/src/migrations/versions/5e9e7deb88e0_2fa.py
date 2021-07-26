"""2fa

Revision ID: 5e9e7deb88e0
Revises: da0181bec3fb
Create Date: 2021-07-22 14:39:54.745432

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e9e7deb88e0'
down_revision = 'da0181bec3fb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'UserRole', ['id'])
    op.add_column('user', sa.Column('active_2FA', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('is_verified', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('totp_secret', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'totp_secret')
    op.drop_column('user', 'is_verified')
    op.drop_column('user', 'active_2FA')
    op.drop_constraint(None, 'UserRole', type_='unique')
    # ### end Alembic commands ###
