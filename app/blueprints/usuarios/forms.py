from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Optional, Length


class UsuarioForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[Optional(), Length(min=6)])
    is_admin = BooleanField('Administrador')
    activo = BooleanField('Activo', default=True)
    puede_clientes = BooleanField('Clientes')
    puede_lotes = BooleanField('Lotes')
    puede_productos = BooleanField('Productos')
    puede_recetas = BooleanField('Recetas')
