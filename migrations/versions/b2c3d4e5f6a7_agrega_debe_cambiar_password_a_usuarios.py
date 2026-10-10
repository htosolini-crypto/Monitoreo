"""Agrega debe_cambiar_password a usuarios

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-10-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # server_default false: los usuarios que ya existen no quedan obligados a cambiar su contraseña.
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('debe_cambiar_password', sa.Boolean(), server_default=sa.false(), nullable=False)
        )


def downgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_column('debe_cambiar_password')
