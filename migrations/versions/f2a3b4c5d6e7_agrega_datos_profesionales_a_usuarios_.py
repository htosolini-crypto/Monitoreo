"""Agrega datos profesionales a usuarios y usuario_id a recetas

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2026-09-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2a3b4c5d6e7'
down_revision = 'e1f2a3b4c5d6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nombre_completo', sa.String(length=150), nullable=True))
        batch_op.add_column(sa.Column('matricula', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('cuit', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('domicilio', sa.String(length=150), nullable=True))
        batch_op.add_column(sa.Column('telefono', sa.String(length=50), nullable=True))

    with op.batch_alter_table('recetas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('usuario_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('fk_recetas_usuario_id', 'usuarios', ['usuario_id'], ['id'])


def downgrade():
    with op.batch_alter_table('recetas', schema=None) as batch_op:
        batch_op.drop_constraint('fk_recetas_usuario_id', type_='foreignkey')
        batch_op.drop_column('usuario_id')

    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_column('telefono')
        batch_op.drop_column('domicilio')
        batch_op.drop_column('cuit')
        batch_op.drop_column('matricula')
        batch_op.drop_column('nombre_completo')
