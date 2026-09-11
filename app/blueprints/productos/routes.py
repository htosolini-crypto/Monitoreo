from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.blueprints.productos import bp
from app.blueprints.productos.forms import ProductoForm
from app.decorators import tiene_permiso_modulo
from app.models import Producto, Parametro, PrincipioActivo


@bp.before_request
def _verificar_permiso():
    if not current_user.is_authenticated:
        return None
    if not tiene_permiso_modulo('puede_productos'):
        flash('No tenés permiso para acceder a Productos.', 'danger')
        return redirect(url_for('dashboard'))


def _cargar_choices(form):
    form.unidad.choices = Parametro.opciones('unidad_producto')
    form.id_insumo.choices = Parametro.opciones('tipo_insumo')
    form.principio_activo_id.choices = [
        (p.id, p.nombre) for p in PrincipioActivo.query.order_by(PrincipioActivo.nombre.asc()).all()
    ]


@bp.route('/')
@login_required
def listar():
    productos = Producto.query.order_by(Producto.id.desc()).all()
    return render_template('productos/listar.html', productos=productos)


@bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    form = ProductoForm()
    _cargar_choices(form)
    if form.validate_on_submit():
        producto = Producto()
        form.populate_obj(producto)
        db.session.add(producto)
        db.session.commit()
        flash('Producto registrado correctamente.', 'success')
        return redirect(url_for('productos.listar'))
    return render_template('productos/form.html', form=form, titulo='Nuevo Producto')


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    producto = Producto.query.get_or_404(id)
    form = ProductoForm(obj=producto)
    _cargar_choices(form)
    if form.validate_on_submit():
        form.populate_obj(producto)
        db.session.commit()
        flash('Producto actualizado correctamente.', 'success')
        return redirect(url_for('productos.listar'))
    return render_template('productos/form.html', form=form, titulo='Editar Producto')


@bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    producto = Producto.query.get_or_404(id)
    try:
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado correctamente.', 'warning')
    except IntegrityError:
        db.session.rollback()
        flash('No se puede eliminar: el producto está incluido en una o más recetas.', 'danger')
    return redirect(url_for('productos.listar'))
