"""init

Revision ID: aa700508ce66
Revises: 
Create Date: 2023-01-04 15:03:00.711525

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'aa700508ce66'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('model_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tablename', sa.String(length=500), nullable=True),
    sa.Column('item_id', sa.String(length=500), nullable=True),
    sa.Column('action', sa.String(length=500), nullable=True),
    sa.Column('changes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('remarks', sa.String(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('organization',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=500), nullable=True),
    sa.Column('short_name', sa.String(length=500), nullable=True),
    sa.Column('code', sa.String(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('person',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(length=500), nullable=True),
    sa.Column('full_name_en', sa.String(length=500), nullable=True),
    sa.Column('atomized_name', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('sorting_name', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('abbreviated_name', sa.String(length=500), nullable=True),
    sa.Column('preferred_name', sa.String(length=500), nullable=True),
    sa.Column('organization_name', sa.String(length=500), nullable=True),
    sa.Column('is_collector', sa.Boolean(), nullable=True),
    sa.Column('is_identifier', sa.Boolean(), nullable=True),
    sa.Column('source_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('taxon_provider',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('taxon_tree',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=1000), nullable=True),
    sa.Column('memo', sa.String(length=1000), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('article_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=500), nullable=True),
    sa.Column('label', sa.String(length=500), nullable=True),
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('collection',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=500), nullable=True),
    sa.Column('label', sa.String(length=500), nullable=True),
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('related_link_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('label', sa.String(length=500), nullable=True),
    sa.Column('name', sa.String(length=500), nullable=True),
    sa.Column('sort', sa.Integer(), nullable=True),
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('taxon',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rank', sa.String(length=50), nullable=True),
    sa.Column('full_scientific_name', sa.String(length=500), nullable=True),
    sa.Column('first_epithet', sa.String(length=500), nullable=True),
    sa.Column('infraspecific_epithet', sa.String(length=500), nullable=True),
    sa.Column('author', sa.String(length=500), nullable=True),
    sa.Column('canonical_name', sa.String(length=500), nullable=True),
    sa.Column('common_name', sa.String(length=500), nullable=True),
    sa.Column('code', sa.String(length=500), nullable=True),
    sa.Column('tree_id', sa.Integer(), nullable=True),
    sa.Column('provider_id', sa.Integer(), nullable=True),
    sa.Column('provider_source_id', sa.String(length=500), nullable=True),
    sa.Column('is_accepted', sa.Boolean(), nullable=True),
    sa.Column('source_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['provider_id'], ['taxon_provider.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['tree_id'], ['taxon_tree.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=500), nullable=True),
    sa.Column('passwd', sa.String(length=500), nullable=True),
    sa.Column('status', sa.String(length=1), nullable=True),
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('area_class',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=500), nullable=True),
    sa.Column('label', sa.String(length=500), nullable=True),
    sa.Column('sort', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('collection_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['collection_id'], ['collection.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['parent_id'], ['area_class.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('article',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subject', sa.String(length=500), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('publish_date', sa.Date(), nullable=True),
    sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_markdown', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['article_category.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('assertion_type',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=500), nullable=True),
    sa.Column('label', sa.String(length=500), nullable=True),
    sa.Column('target', sa.String(length=50), nullable=True),
    sa.Column('sort', sa.Integer(), nullable=True),
    sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('input_type', sa.String(length=50), nullable=True),
    sa.Column('collection_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['collection_id'], ['collection.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('collection_person_map',
    sa.Column('collection_id', sa.Integer(), nullable=False),
    sa.Column('person_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['collection_id'], ['collection.id'], ),
    sa.ForeignKeyConstraint(['person_id'], ['person.id'], ),
    sa.PrimaryKeyConstraint('collection_id', 'person_id')
    )
    op.create_table('favorite',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('record', sa.String(length=500), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('project',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=500), nullable=True),
    sa.Column('collection_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['collection_id'], ['collection.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('related_link',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=500), nullable=True),
    sa.Column('url', sa.String(length=1000), nullable=True),
    sa.Column('note', sa.String(length=1000), nullable=True),
    sa.Column('status', sa.String(length=4), nullable=True),
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['related_link_category.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('taxon_relation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('child_id', sa.Integer(), nullable=True),
    sa.Column('depth', sa.SmallInteger(), nullable=True),
    sa.ForeignKeyConstraint(['child_id'], ['taxon.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['parent_id'], ['taxon.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('assertion_type_option',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(length=500), nullable=True),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('assertion_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['assertion_type_id'], ['assertion_type.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('entity',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('collect_date', sa.DateTime(), nullable=True),
    sa.Column('collect_date_text', sa.String(length=500), nullable=True),
    sa.Column('collector_id', sa.Integer(), nullable=True),
    sa.Column('field_number', sa.String(length=500), nullable=True),
    sa.Column('companion_text', sa.String(length=500), nullable=True),
    sa.Column('companion_text_en', sa.String(length=500), nullable=True),
    sa.Column('verbatim_locality', sa.String(length=1000), nullable=True),
    sa.Column('locality_text', sa.String(length=1000), nullable=True),
    sa.Column('locality_text_en', sa.String(length=1000), nullable=True),
    sa.Column('altitude', sa.Integer(), nullable=True),
    sa.Column('altitude2', sa.Integer(), nullable=True),
    sa.Column('latitude_decimal', sa.Numeric(precision=9, scale=6), nullable=True),
    sa.Column('longitude_decimal', sa.Numeric(precision=9, scale=6), nullable=True),
    sa.Column('verbatim_latitude', sa.String(length=50), nullable=True),
    sa.Column('verbatim_longitude', sa.String(length=50), nullable=True),
    sa.Column('field_note', sa.Text(), nullable=True),
    sa.Column('field_note_en', sa.Text(), nullable=True),
    sa.Column('proxy_taxon_scientific_name', sa.Text(), nullable=True),
    sa.Column('proxy_taxon_common_name', sa.Text(), nullable=True),
    sa.Column('proxy_taxon_id', sa.Integer(), nullable=True),
    sa.Column('source_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('collection_id', sa.Integer(), nullable=True),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['collection_id'], ['collection.id'], ),
    sa.ForeignKeyConstraint(['collector_id'], ['person.id'], ),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.ForeignKeyConstraint(['proxy_taxon_id'], ['taxon.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_entity_field_number'), 'entity', ['field_number'], unique=False)
    op.create_table('named_area',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=500), nullable=True),
    sa.Column('name_en', sa.String(length=500), nullable=True),
    sa.Column('code', sa.String(length=500), nullable=True),
    sa.Column('area_class_id', sa.Integer(), nullable=True),
    sa.Column('source_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['area_class_id'], ['area_class.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['parent_id'], ['named_area.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('entity_assertion',
    sa.Column('value', sa.String(length=500), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('entity_id', sa.Integer(), nullable=True),
    sa.Column('assertion_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['assertion_type_id'], ['assertion_type.id'], ),
    sa.ForeignKeyConstraint(['entity_id'], ['entity.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('entity_named_area_map',
    sa.Column('entity_id', sa.Integer(), nullable=False),
    sa.Column('named_area_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['entity_id'], ['entity.id'], ),
    sa.ForeignKeyConstraint(['named_area_id'], ['named_area.id'], ),
    sa.PrimaryKeyConstraint('entity_id', 'named_area_id')
    )
    op.create_table('entity_person',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('entity_id', sa.Integer(), nullable=True),
    sa.Column('person_id', sa.Integer(), nullable=True),
    sa.Column('role', sa.String(length=50), nullable=True),
    sa.Column('sequence', sa.Integer(), nullable=True),
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['entity_id'], ['entity.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['person_id'], ['person.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('identification',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('entity_id', sa.Integer(), nullable=True),
    sa.Column('identifier_id', sa.Integer(), nullable=True),
    sa.Column('taxon_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('date_text', sa.String(length=50), nullable=True),
    sa.Column('verification_level', sa.String(length=50), nullable=True),
    sa.Column('sequence', sa.Integer(), nullable=True),
    sa.Column('reference', sa.Text(), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('source_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['entity_id'], ['entity.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['identifier_id'], ['person.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['taxon_id'], ['taxon.id'], ondelete='set NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_identification_taxon_id'), 'identification', ['taxon_id'], unique=False)
    op.create_table('other_field_number',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('entity_id', sa.Integer(), nullable=True),
    sa.Column('value', sa.String(length=500), nullable=True),
    sa.Column('collector_id', sa.Integer(), nullable=True),
    sa.Column('collector_name', sa.String(length=500), nullable=True),
    sa.ForeignKeyConstraint(['collector_id'], ['person.id'], ),
    sa.ForeignKeyConstraint(['entity_id'], ['entity.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('unit',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('catalog_number', sa.String(length=500), nullable=True),
    sa.Column('entity_id', sa.Integer(), nullable=True),
    sa.Column('collection_id', sa.Integer(), nullable=True),
    sa.Column('kind_of_unit', sa.String(length=500), nullable=True),
    sa.Column('accession_number', sa.String(length=500), nullable=True),
    sa.Column('duplication_number', sa.String(length=500), nullable=True),
    sa.Column('preparation_type', sa.String(length=500), nullable=True),
    sa.Column('preparation_date', sa.Date(), nullable=True),
    sa.Column('acquisition_type', sa.String(length=500), nullable=True),
    sa.Column('acquisition_date', sa.DateTime(), nullable=True),
    sa.Column('acquired_from', sa.Integer(), nullable=True),
    sa.Column('acquisition_source_text', sa.Text(), nullable=True),
    sa.Column('type_status', sa.String(length=50), nullable=True),
    sa.Column('typified_name', sa.String(length=500), nullable=True),
    sa.Column('type_reference', sa.String(length=500), nullable=True),
    sa.Column('type_reference_link', sa.String(length=500), nullable=True),
    sa.Column('type_note', sa.String(length=500), nullable=True),
    sa.Column('type_identification_id', sa.Integer(), nullable=True),
    sa.Column('source_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('information_withheld', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['acquired_from'], ['person.id'], ),
    sa.ForeignKeyConstraint(['collection_id'], ['collection.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['entity_id'], ['entity.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['type_identification_id'], ['identification.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_unit_accession_number'), 'unit', ['accession_number'], unique=False)
    op.create_index(op.f('ix_unit_collection_id'), 'unit', ['collection_id'], unique=False)
    op.create_table('multimedia_object',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('unit_id', sa.Integer(), nullable=True),
    sa.Column('multimedia_type', sa.String(length=500), nullable=True),
    sa.Column('title', sa.String(length=500), nullable=True),
    sa.Column('source', sa.String(length=500), nullable=True),
    sa.Column('provider', sa.String(length=500), nullable=True),
    sa.Column('file_url', sa.String(length=500), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('source_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['unit_id'], ['unit.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transaction',
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=500), nullable=True),
    sa.Column('unit_id', sa.Integer(), nullable=True),
    sa.Column('transaction_type', sa.String(length=500), nullable=True),
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.Column('organization_text', sa.String(length=500), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['unit_id'], ['unit.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('unit_assertion',
    sa.Column('value', sa.String(length=500), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('unit_id', sa.Integer(), nullable=True),
    sa.Column('assertion_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['assertion_type_id'], ['assertion_type.id'], ),
    sa.ForeignKeyConstraint(['unit_id'], ['unit.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('unit_mark',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('unit_id', sa.Integer(), nullable=True),
    sa.Column('mark_type', sa.String(length=50), nullable=True),
    sa.Column('mark_text', sa.String(length=500), nullable=True),
    sa.Column('mark_author', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['mark_author'], ['person.id'], ),
    sa.ForeignKeyConstraint(['unit_id'], ['unit.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('unit_mark')
    op.drop_table('unit_assertion')
    op.drop_table('transaction')
    op.drop_table('multimedia_object')
    op.drop_index(op.f('ix_unit_collection_id'), table_name='unit')
    op.drop_index(op.f('ix_unit_accession_number'), table_name='unit')
    op.drop_table('unit')
    op.drop_table('other_field_number')
    op.drop_index(op.f('ix_identification_taxon_id'), table_name='identification')
    op.drop_table('identification')
    op.drop_table('entity_person')
    op.drop_table('entity_named_area_map')
    op.drop_table('entity_assertion')
    op.drop_table('named_area')
    op.drop_index(op.f('ix_entity_field_number'), table_name='entity')
    op.drop_table('entity')
    op.drop_table('assertion_type_option')
    op.drop_table('taxon_relation')
    op.drop_table('related_link')
    op.drop_table('project')
    op.drop_table('favorite')
    op.drop_table('collection_person_map')
    op.drop_table('assertion_type')
    op.drop_table('article')
    op.drop_table('area_class')
    op.drop_table('user')
    op.drop_table('taxon')
    op.drop_table('related_link_category')
    op.drop_table('collection')
    op.drop_table('article_category')
    op.drop_table('taxon_tree')
    op.drop_table('taxon_provider')
    op.drop_table('person')
    op.drop_table('organization')
    op.drop_table('model_history')
    # ### end Alembic commands ###
