from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.blueprints.principios_activos import bp
from app.blueprints.principios_activos.forms import PrincipioActivoForm
from app.decorators import tiene_permiso_modulo
from app.models import PrincipioActivo


@bp.before_request
def _verificar_permiso():
    if not current_user.is_authenticated:
        return None
    if not tiene_permiso_modulo('puede_productos'):
        flash('No tenés permiso para acceder a Principios Activos.', 'danger')
        return redirect(url_for('dashboard'))


@bp.route('/')
@login_required
def listar():
    principios = PrincipioActivo.query.order_by(PrincipioActivo.nombre.asc()).all()
    return render_template('principios_activos/listar.html', principios=principios)


@bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    form = PrincipioActivoForm()
    if form.validate_on_submit():
        principio = PrincipioActivo(nombre=form.nombre.data)
        db.session.add(principio)
        try:
            db.session.commit()
            flash('Principio activo registrado correctamente.', 'success')
            return redirect(url_for('principios_activos.listar'))
        except IntegrityError:
            db.session.rollback()
            flash('Ya existe un principio activo con ese nombre.', 'danger')
    return render_template('principios_activos/form.html', form=form, titulo='Nuevo Principio Activo')


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    principio = PrincipioActivo.query.get_or_404(id)
    form = PrincipioActivoForm(obj=principio)
    if form.validate_on_submit():
        principio.nombre = form.nombre.data
        try:
            db.session.commit()
            flash('Principio activo actualizado correctamente.', 'success')
            return redirect(url_for('principios_activos.listar'))
        except IntegrityError:
            db.session.rollback()
            flash('Ya existe un principio activo con ese nombre.', 'danger')
    return render_template('principios_activos/form.html', form=form, titulo='Editar Principio Activo')


@bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    principio = PrincipioActivo.query.get_or_404(id)
    try:
        db.session.delete(principio)
        db.session.commit()
        flash('Principio activo eliminado correctamente.', 'warning')
    except IntegrityError:
        db.session.rollback()
        flash('No se puede eliminar: el principio activo está siendo usado por uno o más productos.', 'danger')
    return redirect(url_for('principios_activos.listar'))
