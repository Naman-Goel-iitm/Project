"""sponsor table active filed

Revision ID: 33271de45319
Revises: 616d24bb1348
Create Date: 2024-08-12 12:23:35.094272

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '33271de45319'
down_revision = '616d24bb1348'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('demo')
    with op.batch_alter_table('sponsor', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('is_flagged', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sponsor', schema=None) as batch_op:
        batch_op.drop_column('is_flagged')
        batch_op.drop_column('is_active')

    op.create_table('demo',
    sa.Column('ID', sa.INTEGER(), nullable=True),
    sa.Column('Name', sa.VARCHAR(length=20), nullable=True),
    sa.Column('Hint', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('ID')
    )
    # ### end Alembic commands ###
