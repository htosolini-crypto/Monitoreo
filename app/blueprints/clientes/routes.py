from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.blueprints.clientes import bp
from app.blueprints.clientes.forms import ClienteForm
from app.decorators import tiene_permiso_modulo
from app.models import Cliente, Parametro


@bp.before_request
def _verificar_permiso():
    if not current_user.is_authenticated:
        return None
    if not tiene_permiso_modulo('puede_clientes'):
        flash('No tenés permiso para acceder a Clientes.', 'danger')
        return redirect(url_for('dashboard'))


def _cargar_choices(form):
    form.id_coniva.choices = [('', '-- Seleccionar --')] + Parametro.opciones('condicion_iva')


@bp.route('/')
@login_required
def listar():
    clientes = Cliente.query.order_by(Cliente.razon_social.asc()).all()
    return render_template('clientes/listar.html', clientes=clientes)


@bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    form = ClienteForm()
    _cargar_choices(form)
    if form.validate_on_submit():
        cliente = Cliente()
        form.populate_obj(cliente)
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente agregado exitosamente.', 'success')
        return redirect(url_for('clientes.listar'))
    return render_template('clientes/form.html', form=form, titulo='Nuevo Cliente')


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    cliente = Cliente.query.get_or_404(id)
    form = ClienteForm(obj=cliente)
    _cargar_choices(form)
    if form.validate_on_submit():
        form.populate_obj(cliente)
        db.session.commit()
        flash('Cliente actualizado correctamente.', 'success')
        return redirect(url_for('clientes.listar'))
    return render_template('clientes/form.html', form=form, titulo='Editar Cliente')


@bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    cliente = Cliente.query.get_or_404(id)
    try:
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente eliminado correctamente.', 'warning')
    except IntegrityError:
        db.session.rollback()
        flash('No se puede eliminar: el cliente tiene lotes con recetas asociadas.', 'danger')
    return redirect(url_for('clientes.listar'))
