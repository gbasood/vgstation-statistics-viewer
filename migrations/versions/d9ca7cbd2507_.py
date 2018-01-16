"""Fix devastation range naming

Revision ID: d9ca7cbd2507
Revises: c608894207f9
Create Date: 2018-01-15 12:49:42.352557

"""
from alembic import op

# import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9ca7cbd2507'
down_revision = 'c608894207f9'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('explosion') as batch_op:
        batch_op.alter_column('devestation_range', new_column_name='devastation_range')


def downgrade():
    with op.batch_alter_table('explosion') as batch_op:
        batch_op.alter_column('devastation_range', new_column_name='devestation_range')
