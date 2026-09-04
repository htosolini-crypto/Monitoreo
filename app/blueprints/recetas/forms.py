from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Optional


class RecetaForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    lote_id = SelectField('Lote', coerce=int, validators=[DataRequired()])
    hectareas = FloatField('Hectáreas', validators=[DataRequired(), NumberRange(min=0)])
    observaciones = TextAreaField('Observaciones', validators=[Optional()])
