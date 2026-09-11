from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.blueprints.campanias import bp
from app.blueprints.campanias.forms import CampaniaForm
from app.decorators import tiene_permiso_modulo
from app.models import Campania, Lote, Cliente


@bp.before_request
def _verificar_permiso():
    if not current_user.is_authenticated:
        return None
    # Excepción: lo usa el combo dinámico de Recetas, que ya valida su propio permiso.
    if request.endpoint == 'campanias.por_lote':
        return None
    if not tiene_permiso_modulo('puede_lotes'):
        flash('No tenés permiso para acceder a Campañas.', 'danger')
        return redirect(url_for('dashboard'))


def _cargar_choices(form, cliente_id=None):
    clientes = Cliente.query.order_by(Cliente.razon_social.asc()).all()
    form.cliente_id.choices = [(c.id, c.razon_social) for c in clientes]

    lotes_query = Lote.query.order_by(Lote.nombre.asc())
    if cliente_id:
        lotes_query = lotes_query.filter_by(cliente_id=cliente_id)
    form.lote_id.choices = [(l.id, l.nombre) for l in lotes_query.all()]


@bp.route('/')
@login_required
def listar():
    cliente_id = request.args.get('cliente_id', type=int)
    lote_id = request.args.get('lote_id', type=int)
    query = Campania.query.join(Lote)
    if cliente_id:
        query = query.filter(Lote.cliente_id == cliente_id)
    if lote_id:
        query = query.filter(Campania.lote_id == lote_id)
    campanias = query.order_by(Campania.id.desc()).all()
    clientes = Cliente.query.order_by(Cliente.razon_social.asc()).all()
    lote_filtro = Lote.query.get(lote_id) if lote_id else None
    return render_template(
        'campanias/listar.html',
        campanias=campanias,
        clientes=clientes,
        cliente_filtro=cliente_id,
        lote_filtro=lote_filtro,
    )


@bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    form = CampaniaForm()
    cliente_id = request.form.get('cliente_id', type=int) or request.args.get('cliente_id', type=int)
    _cargar_choices(form, cliente_id)

    if request.method == 'GET':
        lote_id_prefill = request.args.get('lote_id', type=int)
        if lote_id_prefill:
            form.lote_id.data = lote_id_prefill

    if form.validate_on_submit():
        campania = Campania(
            lote_id=form.lote_id.data,
            nombre=form.nombre.data,
            cultivo=form.cultivo.data,
            variedad=form.variedad.data,
            fecha_siembra=form.fecha_siembra.data,
            fecha_cosecha=form.fecha_cosecha.data,
            observaciones=form.observaciones.data,
            activo=form.activo.data,
        )
        db.session.add(campania)
        db.session.commit()
        flash('Campaña registrada correctamente.', 'success')
        return redirect(url_for('campanias.listar'))

    return render_template('campanias/form.html', form=form, titulo='Nueva Campaña')


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    campania = Campania.query.get_or_404(id)
    form = CampaniaForm(obj=campania)
    if request.method == 'GET':
        form.cliente_id.data = campania.lote.cliente_id
    cliente_id = request.form.get('cliente_id', type=int) or form.cliente_id.data
    _cargar_choices(form, cliente_id)

    if form.validate_on_submit():
        campania.lote_id = form.lote_id.data
        campania.nombre = form.nombre.data
        campania.cultivo = form.cultivo.data
        campania.variedad = form.variedad.data
        campania.fecha_siembra = form.fecha_siembra.data
        campania.fecha_cosecha = form.fecha_cosecha.data
        campania.observaciones = form.observaciones.data
        campania.activo = form.activo.data
        db.session.commit()
        flash('Campaña actualizada correctamente.', 'success')
        return redirect(url_for('campanias.listar'))

    return render_template('campanias/form.html', form=form, titulo='Editar Campaña')


@bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    campania = Campania.query.get_or_404(id)
    try:
        db.session.delete(campania)
        db.session.commit()
        flash('Campaña eliminada correctamente.', 'warning')
    except IntegrityError:
        db.session.rollback()
        flash('No se puede eliminar: la campaña tiene recetas asociadas.', 'danger')
    return redirect(url_for('campanias.listar'))


@bp.route('/por_lote/<int:lote_id>')
@login_required
def por_lote(lote_id):
    """Devuelve las campañas activas de un lote en JSON, para el combo dinámico del form de recetas."""
    campanias = Campania.query.filter_by(lote_id=lote_id, activo=True).order_by(Campania.id.desc()).all()
    return {
        'campanias': [{'id': c.id, 'nombre': f'{c.nombre} ({c.cultivo})'} for c in campanias]
    }
