"""org.settings

Revision ID: a4d050f81a5a
Revises: eda150eeea0c
Create Date: 2023-05-29 19:40:44.853757

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a4d050f81a5a'
down_revision = 'eda150eeea0c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('organization', sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('organization', 'settings')
    # ### end Alembic commands ###
