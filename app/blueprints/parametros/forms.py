from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Optional, NumberRange


class ParametroForm(FlaskForm):
    categoria_existente = SelectField('Categoría existente', validators=[Optional()])
    categoria_nueva = StringField(
        '...o cargá una categoría nueva',
        validators=[Optional()],
        render_kw={'placeholder': 'Ej: condicion_iva, unidad_producto, tipo_insumo'},
    )
    valor = StringField('Valor', validators=[DataRequired()])
    abreviatura = StringField('Abreviatura', validators=[Optional()], render_kw={'placeholder': 'Ej: kg, L, IVA RI'})
    orden = IntegerField('Orden', validators=[Optional(), NumberRange(min=0)], default=0)
    activo = BooleanField('Activo', default=True)
