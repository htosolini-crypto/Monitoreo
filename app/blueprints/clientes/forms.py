from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Optional, Email, ValidationError

from app.utils import validar_cuit


def cuit_valido(form, field):
    if field.data and not validar_cuit(field.data):
        raise ValidationError('El CUIT ingresado no es válido (dígito verificador incorrecto).')


class ClienteForm(FlaskForm):
    cuit = StringField('CUIT', validators=[Optional(), cuit_valido])
    razon_social = StringField('Razón Social', validators=[DataRequired()])
    domicilio = StringField('Domicilio', validators=[Optional()])
    numero = StringField('Número', validators=[Optional()])
    codigo_postal = StringField('Código Postal', validators=[Optional()])
    localidad = StringField('Localidad', validators=[Optional()])
    telefono = StringField('Teléfono', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    id_coniva = SelectField('Condición IVA', validators=[Optional()])
    enlace_maps = StringField(
        'Enlace de Google Maps',
        validators=[Optional()],
        render_kw={'placeholder': 'Pegá acá el enlace que copiaste de Google Maps'},
    )
