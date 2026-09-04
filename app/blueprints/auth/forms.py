from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Ingresar')


class SolicitarRecuperacionForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar instrucciones')


class RestablecerPasswordForm(FlaskForm):
    password = PasswordField('Nueva contraseña', validators=[DataRequired(), Length(min=6)])
    confirmar_password = PasswordField(
        'Confirmar contraseña',
        validators=[DataRequired(), EqualTo('password', message='Las contraseñas no coinciden.')],
    )
    submit = SubmitField('Restablecer contraseña')
