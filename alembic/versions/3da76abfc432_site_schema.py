"""site-schema

Revision ID: 3da76abfc432
Revises: 4c228755cffb
Create Date: 2024-06-18 05:09:31.292914

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision = '3da76abfc432'
down_revision = '4c228755cffb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('organization', 'domain')
    op.drop_column('organization', 'is_site')
    op.drop_column('organization', 'settings')
    op.drop_column('organization', 'subdomain')
    op.drop_column('organization', 'description')
    op.drop_column('organization', 'ark_nma')
    op.drop_column('organization', 'logo_url')
    op.add_column('site', sa.Column('title', sa.String(length=500), nullable=True))
    op.add_column('site', sa.Column('title_en', sa.String(length=500), nullable=True))
    op.add_column('site', sa.Column('logo_url', sa.String(length=500), nullable=True))
    op.add_column('site', sa.Column('description', sa.Text(), nullable=True))
    op.alter_column('site', 'name',
               existing_type=sa.VARCHAR(length=500),
               type_=sa.String(length=50),
               existing_nullable=True)
    op.drop_column('site', 'name_en')
    op.drop_column('site', 'short_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('site', sa.Column('short_name', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.add_column('site', sa.Column('name_en', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.alter_column('site', 'name',
               existing_type=sa.String(length=50),
               type_=sa.VARCHAR(length=500),
               existing_nullable=True)
    op.drop_column('site', 'description')
    op.drop_column('site', 'logo_url')
    op.drop_column('site', 'title_en')
    op.drop_column('site', 'title')
    op.add_column('organization', sa.Column('logo_url', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.add_column('organization', sa.Column('ark_nma', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.add_column('organization', sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('organization', sa.Column('subdomain', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('organization', sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('organization', sa.Column('is_site', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('organization', sa.Column('domain', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
