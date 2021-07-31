"""insert roles

Revision ID: 17019afe0af4
Revises: 59b3e0f5d5fd
Create Date: 2021-07-15 16:02:49.290704

"""
import models
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '17019afe0af4'
down_revision = '59b3e0f5d5fd'
branch_labels = None
depends_on = None


def upgrade():
    # Initial data
    op.bulk_insert(
        models.Role.__table__,
        [
            {
                "name": "user",
                "permissions": 1,
                "default": True,
            },
            {
                "name": "premium",
                "permissions": 3,
                "default": False,
            },
            {
                "name": "superuser",
                "permissions": 7,
                "default": False,
            },
        ],
    )

def downgrade():
    pass
