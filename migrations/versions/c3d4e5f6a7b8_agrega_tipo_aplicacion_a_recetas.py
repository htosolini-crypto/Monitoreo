"""Agrega tipo_aplicacion_id a recetas

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-10-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None

TIPOS_APLICACION = ['Terrestre', 'Dron', 'Avión']


def upgrade():
    conn = op.get_bind()

    # En una base que ya tiene parámetros se cargan los ítems acá; en una base nueva los carga
    # seed-parametros junto con el resto de las categorías.
    if conn.execute(sa.text('SELECT COUNT(*) FROM parametros')).scalar():
        for orden, valor in enumerate(TIPOS_APLICACION):
            existe = conn.execute(
                sa.text("SELECT 1 FROM parametros WHERE categoria = 'tipo_aplicacion' AND valor = :valor"),
                {'valor': valor},
            ).scalar()
            if not existe:
                conn.execute(
                    sa.text(
                        "INSERT INTO parametros (categoria, valor, orden, activo) "
                        "VALUES ('tipo_aplicacion', :valor, :orden, :activo)"
                    ),
                    {'valor': valor, 'orden': orden, 'activo': True},
                )

    with op.batch_alter_table('recetas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tipo_aplicacion_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_recetas_tipo_aplicacion_id', 'parametros', ['tipo_aplicacion_id'], ['id'])

    # Las recetas que ya existen quedan como Terrestre (primer ítem de la categoría).
    conn.execute(sa.text(
        "UPDATE recetas SET tipo_aplicacion_id = ("
        "SELECT id FROM parametros WHERE categoria = 'tipo_aplicacion' AND valor = 'Terrestre')"
    ))

    with op.batch_alter_table('recetas', schema=None) as batch_op:
        batch_op.alter_column('tipo_aplicacion_id', existing_type=sa.Integer(), nullable=False)


def downgrade():
    with op.batch_alter_table('recetas', schema=None) as batch_op:
        batch_op.drop_constraint('fk_recetas_tipo_aplicacion_id', type_='foreignkey')
        batch_op.drop_column('tipo_aplicacion_id')
