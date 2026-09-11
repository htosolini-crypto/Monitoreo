from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class PrincipioActivoForm(FlaskForm):
    nombre = StringField('Principio Activo', validators=[DataRequired()])
