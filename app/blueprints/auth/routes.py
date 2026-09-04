from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message

from app.blueprints.auth import bp
from app.blueprints.auth.forms import LoginForm, SolicitarRecuperacionForm, RestablecerPasswordForm
from app.extensions import db, mail
from app.models import Usuario


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(usuario=form.usuario.data).first()
        if usuario and usuario.activo and usuario.check_password(form.password.data):
            login_user(usuario, remember=form.remember.data)
            return redirect(url_for('dashboard'))
        flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    form = SolicitarRecuperacionForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and usuario.activo:
            token = usuario.generar_token_reset()
            enlace = url_for('auth.restablecer', token=token, _external=True)
            try:
                html_content = render_template(
                    'auth/email_recuperacion.html', usuario=usuario, enlace=enlace
                )
                msg = Message(
                    subject='Recuperación de acceso - Sistema de Gestión y Monitoreo Agronómico',
                    recipients=[usuario.email],
                    html=html_content,
                )
                mail.send(msg)
            except Exception:
                pass

        flash(
            'Si el email ingresado está registrado, vas a recibir instrucciones para recuperar tu acceso.',
            'info',
        )
        return redirect(url_for('auth.login'))

    return render_template('auth/recuperar.html', form=form)


@bp.route('/restablecer/<token>', methods=['GET', 'POST'])
def restablecer(token):
    usuario = Usuario.verificar_token_reset(token)
    if not usuario or not usuario.activo:
        flash('El enlace de recuperación es inválido o expiró. Solicitá uno nuevo.', 'danger')
        return redirect(url_for('auth.recuperar'))

    form = RestablecerPasswordForm()
    if form.validate_on_submit():
        usuario.set_password(form.password.data)
        db.session.commit()
        flash('Tu contraseña fue actualizada. Ya podés iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/restablecer.html', form=form, usuario=usuario)
