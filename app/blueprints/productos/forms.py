from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField
from wtforms.validators import DataRequired, NumberRange


class ProductoForm(FlaskForm):
    denominacion_comercial = StringField('Denominación Comercial', validators=[DataRequired()])
    principio_activo_id = SelectField('Principio Activo', coerce=int, validators=[DataRequired()])
    concentracion = FloatField('Concentración (%)', validators=[DataRequired(), NumberRange(min=0)])
    marca = StringField('Marca', validators=[DataRequired()])
    unidad = SelectField('Unidad', validators=[DataRequired()])
    precio = FloatField('Precio (por unidad)', validators=[DataRequired(), NumberRange(min=0)])
    id_insumo = SelectField('Tipo de Insumo', validators=[DataRequired()])
