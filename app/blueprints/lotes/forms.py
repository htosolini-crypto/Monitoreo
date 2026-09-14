from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, FloatField, SelectField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Optional


class LoteForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    nombre = StringField('Nombre del Lote', validators=[DataRequired()])
    superficie_ha = FloatField('Superficie (ha)', validators=[DataRequired(), NumberRange(min=0)])
    enlace_maps = StringField(
        'Enlace de Google Maps',
        validators=[Optional()],
        render_kw={'placeholder': 'Pegá acá el enlace que copiaste de Google Maps'},
    )
    activo = BooleanField('Activo', default=True)


ORGANOS = [
    ('auto', 'Detectar automáticamente'),
    ('leaf', 'Hoja'),
    ('flower', 'Flor'),
    ('fruit', 'Fruto'),
    ('bark', 'Corteza/Tallo'),
]


class IdentificarPlantaForm(FlaskForm):
    imagen = FileField('Foto de la planta', validators=[
        FileRequired('Seleccioná una foto.'),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Solo se permiten imágenes JPG o PNG.'),
    ])
    organo = SelectField('¿Qué parte de la planta muestra la foto?', choices=ORGANOS, default='auto')
