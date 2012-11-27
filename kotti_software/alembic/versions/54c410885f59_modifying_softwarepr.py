"""modifying softwareprojects table

Revision ID: 1a5ad7ba8e98
Revises: None
Create Date: 2012-11-27 12:14:12.868446

"""

# revision identifiers, used by Alembic.
revision = '1a5ad7ba8e98'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('desc_handling_choice', sa.Column('desc_handling_choice', sa.String(1000)))
    op.add_column('date_handling_choice', sa.Column('date_handling_choice', sa.String(1000)))


def downgrade():
    pass
