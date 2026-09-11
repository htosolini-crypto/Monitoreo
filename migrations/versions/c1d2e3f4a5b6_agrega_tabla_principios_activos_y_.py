"""Agrega tabla principios_activos y migra el dato desde productos

Revision ID: c1d2e3f4a5b6
Revises: 47561bb6e179
Create Date: 2026-09-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1d2e3f4a5b6'
down_revision = '47561bb6e179'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'principios_activos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=150), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre'),
    )

    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('principio_activo_id', sa.Integer(), nullable=True))

    bind = op.get_bind()
    principios_activos = sa.table(
        'principios_activos',
        sa.column('id', sa.Integer()),
        sa.column('nombre', sa.String()),
    )
    productos = sa.table(
        'productos',
        sa.column('id', sa.Integer()),
        sa.column('principio_activo', sa.String()),
        sa.column('principio_activo_id', sa.Integer()),
    )

    nombres = bind.execute(
        sa.select(productos.c.principio_activo).distinct()
    ).fetchall()
    for (nombre,) in nombres:
        if nombre:
            bind.execute(principios_activos.insert().values(nombre=nombre))

    filas = bind.execute(sa.select(principios_activos.c.id, principios_activos.c.nombre)).fetchall()
    for id_, nombre in filas:
        bind.execute(
            productos.update()
            .where(productos.c.principio_activo == nombre)
            .values(principio_activo_id=id_)
        )

    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.alter_column('principio_activo_id', nullable=False)
        batch_op.create_foreign_key(
            'fk_productos_principio_activo_id', 'principios_activos', ['principio_activo_id'], ['id']
        )
        batch_op.drop_column('principio_activo')


def downgrade():
    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('principio_activo', sa.String(length=150), nullable=True))

    bind = op.get_bind()
    principios_activos = sa.table(
        'principios_activos',
        sa.column('id', sa.Integer()),
        sa.column('nombre', sa.String()),
    )
    productos = sa.table(
        'productos',
        sa.column('id', sa.Integer()),
        sa.column('principio_activo', sa.String()),
        sa.column('principio_activo_id', sa.Integer()),
    )
    filas = bind.execute(sa.select(principios_activos.c.id, principios_activos.c.nombre)).fetchall()
    for id_, nombre in filas:
        bind.execute(
            productos.update()
            .where(productos.c.principio_activo_id == id_)
            .values(principio_activo=nombre)
        )

    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.alter_column('principio_activo', nullable=False)
        batch_op.drop_constraint('fk_productos_principio_activo_id', type_='foreignkey')
        batch_op.drop_column('principio_activo_id')

    op.drop_table('principios_activos')
