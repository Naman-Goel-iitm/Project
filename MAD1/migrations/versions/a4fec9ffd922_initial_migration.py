"""Initial migration.

Revision ID: a4fec9ffd922
Revises: 
Create Date: 2024-08-10 12:07:52.914435

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4fec9ffd922'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('influencer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('platform', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('platform_username', sa.String(length=120), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('influencer', schema=None) as batch_op:
        batch_op.drop_column('platform_username')
        batch_op.drop_column('platform')

    # ### end Alembic commands ###
