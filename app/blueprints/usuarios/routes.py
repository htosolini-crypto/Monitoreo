from flask import render_template, redirect, url_for, flash
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.blueprints.usuarios import bp
from app.blueprints.usuarios.forms import UsuarioForm
from app.decorators import admin_required
from app.models import Usuario


def _aplicar_datos(usuario, form, requerir_password):
    usuario.usuario = form.usuario.data
    usuario.nombre_completo = form.nombre_completo.data
    usuario.email = form.email.data
    usuario.matricula = form.matricula.data
    usuario.cuit = form.cuit.data
    usuario.domicilio = form.domicilio.data
    usuario.telefono = form.telefono.data
    usuario.is_admin = form.is_admin.data
    usuario.activo = form.activo.data
    usuario.puede_clientes = form.puede_clientes.data
    usuario.puede_lotes = form.puede_lotes.data
    usuario.puede_productos = form.puede_productos.data
    usuario.puede_recetas = form.puede_recetas.data

    if form.password.data:
        usuario.set_password(form.password.data)
    elif requerir_password:
        form.password.errors.append('La contraseña es obligatoria para un usuario nuevo.')
        return False
    return True


@bp.route('/')
@admin_required
def listar():
    usuarios = Usuario.query.order_by(Usuario.usuario.asc()).all()
    return render_template('usuarios/listar.html', usuarios=usuarios)


@bp.route('/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo():
    form = UsuarioForm()
    if form.validate_on_submit():
        usuario = Usuario()
        if _aplicar_datos(usuario, form, requerir_password=True):
            try:
                db.session.add(usuario)
                db.session.commit()
                flash('Usuario creado correctamente.', 'success')
                return redirect(url_for('usuarios.listar'))
            except IntegrityError:
                db.session.rollback()
                flash('Ya existe un usuario con ese nombre de usuario o email.', 'danger')
    return render_template('usuarios/form.html', form=form, titulo='Nuevo Usuario')


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar(id):
    usuario = Usuario.query.get_or_404(id)
    form = UsuarioForm(obj=usuario)
    if form.validate_on_submit():
        if usuario.id == current_user.id and not form.is_admin.data:
            flash('No podés quitarte a vos mismo el rol de administrador.', 'danger')
        elif _aplicar_datos(usuario, form, requerir_password=False):
            try:
                db.session.commit()
                flash('Usuario actualizado correctamente.', 'success')
                return redirect(url_for('usuarios.listar'))
            except IntegrityError:
                db.session.rollback()
                flash('Ya existe un usuario con ese nombre de usuario o email.', 'danger')
    return render_template('usuarios/form.html', form=form, titulo='Editar Usuario', usuario=usuario)


@bp.route('/<int:id>/eliminar', methods=['POST'])
@admin_required
def eliminar(id):
    usuario = Usuario.query.get_or_404(id)

    if usuario.id == current_user.id:
        flash('No podés eliminar tu propio usuario.', 'danger')
        return redirect(url_for('usuarios.listar'))

    if usuario.is_admin and Usuario.query.filter_by(is_admin=True).count() <= 1:
        flash('No se puede eliminar el último usuario administrador.', 'danger')
        return redirect(url_for('usuarios.listar'))

    try:
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuario eliminado correctamente.', 'warning')
    except IntegrityError:
        db.session.rollback()
        flash('No se puede eliminar ese usuario.', 'danger')
    return redirect(url_for('usuarios.listar'))
