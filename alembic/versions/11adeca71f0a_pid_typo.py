"""pid typo

Revision ID: 11adeca71f0a
Revises: 5239ef1d08b2
Create Date: 2023-12-11 14:16:20.161240

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11adeca71f0a'
down_revision = '5239ef1d08b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('unit', sa.Column('persistent_identifier', sa.String(length=500), nullable=True))
    op.drop_column('unit', 'persistent_idenfier')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('unit', sa.Column('persistent_idenfier', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.drop_column('unit', 'persistent_identifier')
    # ### end Alembic commands ###
