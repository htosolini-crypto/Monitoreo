"""Agrega tabla campanias, la relaciona a lotes y recetas, elimina lotes.cultivo

Revision ID: d7e8f9a0b1c2
Revises: c1d2e3f4a5b6
Create Date: 2026-09-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7e8f9a0b1c2'
down_revision = 'c1d2e3f4a5b6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'campanias',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lote_id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=20), nullable=False),
        sa.Column('cultivo', sa.String(length=100), nullable=False),
        sa.Column('variedad', sa.String(length=100), nullable=True),
        sa.Column('fecha_siembra', sa.Date(), nullable=True),
        sa.Column('fecha_cosecha', sa.Date(), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.ForeignKeyConstraint(['lote_id'], ['lotes.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    with op.batch_alter_table('lotes', schema=None) as batch_op:
        batch_op.drop_column('cultivo')

    with op.batch_alter_table('recetas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('campania_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('fk_recetas_campania_id', 'campanias', ['campania_id'], ['id'])


def downgrade():
    with op.batch_alter_table('recetas', schema=None) as batch_op:
        batch_op.drop_constraint('fk_recetas_campania_id', type_='foreignkey')
        batch_op.drop_column('campania_id')

    with op.batch_alter_table('lotes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cultivo', sa.String(length=100), nullable=True))

    op.drop_table('campanias')
