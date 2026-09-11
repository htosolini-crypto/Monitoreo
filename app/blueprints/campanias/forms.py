from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, DateField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Optional


class CampaniaForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    lote_id = SelectField('Lote', coerce=int, validators=[DataRequired()])
    nombre = StringField('Campaña', validators=[DataRequired()], render_kw={'placeholder': 'Ej: 2026/2027'})
    cultivo = StringField('Cultivo', validators=[DataRequired()])
    variedad = StringField('Variedad', validators=[Optional()])
    fecha_siembra = DateField('Fecha de Siembra', validators=[Optional()], render_kw={'type': 'date'})
    fecha_cosecha = DateField('Fecha de Cosecha', validators=[Optional()], render_kw={'type': 'date'})
    observaciones = TextAreaField('Observaciones', validators=[Optional()])
    activo = BooleanField('Campaña Activa', default=True)
