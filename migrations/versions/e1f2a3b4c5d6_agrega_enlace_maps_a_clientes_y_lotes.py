"""Agrega enlace_maps a clientes y lotes

Revision ID: e1f2a3b4c5d6
Revises: d7e8f9a0b1c2
Create Date: 2026-09-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1f2a3b4c5d6'
down_revision = 'd7e8f9a0b1c2'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('clientes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('enlace_maps', sa.String(length=500), nullable=True))

    with op.batch_alter_table('lotes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('enlace_maps', sa.String(length=500), nullable=True))


def downgrade():
    with op.batch_alter_table('lotes', schema=None) as batch_op:
        batch_op.drop_column('enlace_maps')

    with op.batch_alter_table('clientes', schema=None) as batch_op:
        batch_op.drop_column('enlace_maps')
