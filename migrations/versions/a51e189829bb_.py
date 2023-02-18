"""empty message

Revision ID: a51e189829bb
Revises: 2ba9d37060b6
Create Date: 2023-02-12 12:53:17.611269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a51e189829bb'
down_revision = '2ba9d37060b6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('dark_them')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dark_them', sa.VARCHAR(length=10), nullable=True))

    # ### end Alembic commands ###