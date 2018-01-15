"""empty message

Revision ID: c608894207f9
Revises: 
Create Date: 2018-01-15 00:43:49.233788

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c608894207f9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('malf_module',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('match',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parsed_file', sa.String(length=255), nullable=False),
    sa.Column('data_version', sa.String(length=45), nullable=True),
    sa.Column('mastermode', sa.String(length=255), nullable=True),
    sa.Column('modes_string', sa.String(length=65535), nullable=True),
    sa.Column('crewscore', sa.Integer(), nullable=True),
    sa.Column('nuked', sa.Boolean(), nullable=True),
    sa.Column('crates_ordered', sa.Integer(), nullable=True),
    sa.Column('blood_spilled', sa.Integer(), nullable=True),
    sa.Column('artifacts_discovered', sa.Integer(), nullable=True),
    sa.Column('tech_total', sa.Integer(), nullable=True),
    sa.Column('mapname', sa.String(), nullable=True),
    sa.Column('borgs_at_roundend', sa.Integer(), nullable=True),
    sa.Column('remaining_heads', sa.Integer(), nullable=True),
    sa.Column('starttime', sa.Integer(), nullable=True),
    sa.Column('endtime', sa.Integer(), nullable=True),
    sa.Column('round_length', sa.Integer(), nullable=True),
    sa.Column('cult_runes_written', sa.Integer(), nullable=True),
    sa.Column('cult_runes_nulled', sa.Integer(), nullable=True),
    sa.Column('cult_runes_fumbled', sa.Integer(), nullable=True),
    sa.Column('cult_converted', sa.Integer(), nullable=True),
    sa.Column('cult_tomes_created', sa.Integer(), nullable=True),
    sa.Column('cult_narsie_summoned', sa.Boolean(), nullable=True),
    sa.Column('cult_narsie_corpses_fed', sa.Integer(), nullable=True),
    sa.Column('cult_surviving_cultists', sa.Integer(), nullable=True),
    sa.Column('cult_deconverted', sa.Integer(), nullable=True),
    sa.Column('xeno_eggs_laid', sa.Integer(), nullable=True),
    sa.Column('xeno_faces_hugged', sa.Integer(), nullable=True),
    sa.Column('xeno_faces_protected', sa.Integer(), nullable=True),
    sa.Column('blob_wins', sa.Boolean(), nullable=True),
    sa.Column('blob_spawned_blob_players', sa.Integer(), nullable=True),
    sa.Column('blob_spores_spawned', sa.Integer(), nullable=True),
    sa.Column('blob_res_generated', sa.Integer(), nullable=True),
    sa.Column('malf_won', sa.Boolean(), nullable=True),
    sa.Column('malf_shunted', sa.Boolean(), nullable=True),
    sa.Column('revsquad_won', sa.Boolean(), nullable=True),
    sa.Column('start_datetime', sa.DateTime(), nullable=True),
    sa.Column('end_datetime', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('parsed_file')
    )
    op.create_index(op.f('ix_match_mastermode'), 'match', ['mastermode'], unique=False)
    op.create_table('revsquad_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('antag_objective',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('match_id', sa.Integer(), nullable=True),
    sa.Column('mindname', sa.String(length=100), nullable=True),
    sa.Column('mindkey', sa.String(length=30), nullable=True),
    sa.Column('special_role', sa.String(length=30), nullable=True),
    sa.Column('objective_type', sa.String(length=45), nullable=True),
    sa.Column('objective_desc', sa.String(), nullable=True),
    sa.Column('objective_succeeded', sa.Boolean(), nullable=True),
    sa.Column('target_name', sa.String(length=100), nullable=True),
    sa.Column('target_role', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['match_id'], ['match.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_antag_objective_match_id'), 'antag_objective', ['match_id'], unique=False)
    op.create_table('badass_bundle_buy',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('match_id', sa.Integer(), nullable=True),
    sa.Column('mindname', sa.String(), nullable=True),
    sa.Column('mindkey', sa.String(length=30), nullable=True),
    sa.Column('traitor_buyer', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['match_id'], ['match.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_badass_bundle_buy_match_id'), 'badass_bundle_buy', ['match_id'], unique=False)
    op.create_table('death',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('match_id', sa.Integer(), nullable=True),
    sa.Column('mindname', sa.String(length=100), nullable=True),
    sa.Column('mindkey', sa.String(length=30), nullable=True),
    sa.Column('typepath', sa.String(length=200), nullable=True),
    sa.Column('special_role', sa.String(length=100), nullable=True),
    sa.Column('assigned_role', sa.String(length=100), nullable=True),
    sa.Column('time_of_death', sa.Integer(), nullable=True),
    sa.Column('death_x', sa.Integer(), nullable=True),
    sa.Column('death_y', sa.Integer(), nullable=True),
    sa.Column('death_z', sa.Integer(), nullable=True),
    sa.Column('damage_brute', sa.Integer(), nullable=True),
    sa.Column('damage_fire', sa.Integer(), nullable=True),
    sa.Column('damage_toxin', sa.Integer(), nullable=True),
    sa.Column('damage_oxygen', sa.Integer(), nullable=True),
    sa.Column('damage_clone', sa.Integer(), nullable=True),
    sa.Column('damage_brain', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['match_id'], ['match.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_death_match_id'), 'death', ['match_id'], unique=False)
    op.create_table('explosion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('match_id', sa.Integer(), nullable=True),
    sa.Column('epicenter_x', sa.Integer(), nullable=True),
    sa.Column('epicenter_y', sa.Integer(), nullable=True),
    sa.Column('epicenter_z', sa.Integer(), nullable=True),
    sa.Column('devestation_range', sa.Integer(), nullable=True),
    sa.Column('heavy_impact_range', sa.Integer(), nullable=True),
    sa.Column('light_impact_range', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['match_id'], ['match.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_explosion_match_id'), 'explosion', ['match_id'], unique=False)
    op.create_table('match_malf_module',
    sa.Column('match_id', sa.Integer(), nullable=False),
    sa.Column('module_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['match_id'], ['match.id'], ),
    sa.ForeignKeyConstraint(['module_id'], ['malf_module.id'], ),
    sa.PrimaryKeyConstraint('match_id', 'module_id')
    )
    op.create_table('match_revsquad_item',
    sa.Column('match_id', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['item_id'], ['revsquad_item.id'], ),
    sa.ForeignKeyConstraint(['match_id'], ['match.id'], ),
    sa.PrimaryKeyConstraint('match_id', 'item_id')
    )
    op.create_table('population_snapshot',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('match_id', sa.Integer(), nullable=True),
    sa.Column('popcount', sa.Integer(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['match_id'], ['match.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_population_snapshot_match_id'), 'population_snapshot', ['match_id'], unique=False)
    op.create_table('survivor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('match_id', sa.Integer(), nullable=True),
    sa.Column('mindname', sa.String(), nullable=True),
    sa.Column('mindkey', sa.String(length=30), nullable=True),
    sa.Column('special_role', sa.String(), nullable=True),
    sa.Column('mob_typepath', sa.String(), nullable=True),
    sa.Column('damage_brute', sa.Integer(), nullable=True),
    sa.Column('damage_fire', sa.Integer(), nullable=True),
    sa.Column('damage_toxin', sa.Integer(), nullable=True),
    sa.Column('damage_oxygen', sa.Integer(), nullable=True),
    sa.Column('damage_clone', sa.Integer(), nullable=True),
    sa.Column('damage_brain', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['match_id'], ['match.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_survivor_match_id'), 'survivor', ['match_id'], unique=False)
    op.create_table('uplink_buy',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('match_id', sa.Integer(), nullable=True),
    sa.Column('mindname', sa.String(), nullable=True),
    sa.Column('mindkey', sa.String(length=30), nullable=True),
    sa.Column('traitor_buyer', sa.Boolean(), nullable=True),
    sa.Column('bundle_path', sa.String(), nullable=True),
    sa.Column('item_path', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['match_id'], ['match.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_uplink_buy_match_id'), 'uplink_buy', ['match_id'], unique=False)
    op.create_table('badass_bundle_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('badass_bundle_id', sa.Integer(), nullable=True),
    sa.Column('item_path', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['badass_bundle_id'], ['badass_bundle_buy.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_badass_bundle_item_badass_bundle_id'), 'badass_bundle_item', ['badass_bundle_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_badass_bundle_item_badass_bundle_id'), table_name='badass_bundle_item')
    op.drop_table('badass_bundle_item')
    op.drop_index(op.f('ix_uplink_buy_match_id'), table_name='uplink_buy')
    op.drop_table('uplink_buy')
    op.drop_index(op.f('ix_survivor_match_id'), table_name='survivor')
    op.drop_table('survivor')
    op.drop_index(op.f('ix_population_snapshot_match_id'), table_name='population_snapshot')
    op.drop_table('population_snapshot')
    op.drop_table('match_revsquad_item')
    op.drop_table('match_malf_module')
    op.drop_index(op.f('ix_explosion_match_id'), table_name='explosion')
    op.drop_table('explosion')
    op.drop_index(op.f('ix_death_match_id'), table_name='death')
    op.drop_table('death')
    op.drop_index(op.f('ix_badass_bundle_buy_match_id'), table_name='badass_bundle_buy')
    op.drop_table('badass_bundle_buy')
    op.drop_index(op.f('ix_antag_objective_match_id'), table_name='antag_objective')
    op.drop_table('antag_objective')
    op.drop_table('revsquad_item')
    op.drop_index(op.f('ix_match_mastermode'), table_name='match')
    op.drop_table('match')
    op.drop_table('malf_module')
    # ### end Alembic commands ###
