"""Add completion_status column with default value

Revision ID: c8c77c53d204
Revises: e53bdfbdefcc
Create Date: 2024-08-11 23:20:33.538969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8c77c53d204'
down_revision = 'e53bdfbdefcc'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ad_request', sa.Column('completion_status', sa.String(length=20), nullable=False, server_default='pending'))

def downgrade():
    op.drop_column('ad_request', 'completion_status')

