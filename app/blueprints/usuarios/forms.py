from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Optional, Length, ValidationError

from app.utils import validar_cuit


def cuit_valido(form, field):
    if field.data and not validar_cuit(field.data):
        raise ValidationError('El CUIT ingresado no es válido (dígito verificador incorrecto).')


class UsuarioForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired()])
    nombre_completo = StringField('Nombre Completo', validators=[Optional()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[Optional(), Length(min=6)])
    matricula = StringField('N° de Matrícula', validators=[Optional()])
    cuit = StringField('CUIT', validators=[Optional(), cuit_valido])
    domicilio = StringField('Domicilio', validators=[Optional()])
    telefono = StringField('Teléfono', validators=[Optional()])
    is_admin = BooleanField('Administrador')
    activo = BooleanField('Activo', default=True)
    puede_clientes = BooleanField('Clientes')
    puede_lotes = BooleanField('Lotes')
    puede_productos = BooleanField('Productos')
    puede_recetas = BooleanField('Recetas')
