from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Optional


class LoteForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    nombre = StringField('Nombre del Lote', validators=[DataRequired()])
    cultivo = StringField('Cultivo', validators=[Optional()])
    superficie_ha = FloatField('Superficie (ha)', validators=[DataRequired(), NumberRange(min=0)])
    latitud = StringField('Latitud', validators=[Optional()])
    longitud = StringField('Longitud', validators=[Optional()])
    activo = BooleanField('Activo', default=True)
