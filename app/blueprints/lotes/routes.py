from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.blueprints.lotes import bp
from app.blueprints.lotes.forms import LoteForm, IdentificarPlantaForm
from app.decorators import tiene_permiso_modulo
from app.models import Lote, Cliente
from app.services.plantnet import identificar_planta, IdentificacionError


@bp.before_request
def _verificar_permiso():
    if not current_user.is_authenticated:
        return None
    # Excepción: lo usa el combo dinámico de Recetas, que ya valida su propio permiso.
    if request.endpoint == 'lotes.por_cliente':
        return None
    if not tiene_permiso_modulo('puede_lotes'):
        flash('No tenés permiso para acceder a Lotes.', 'danger')
        return redirect(url_for('dashboard'))


def _cargar_choices_cliente(form):
    clientes = Cliente.query.order_by(Cliente.razon_social.asc()).all()
    form.cliente_id.choices = [(c.id, c.razon_social) for c in clientes]


@bp.route('/')
@login_required
def listar():
    cliente_id = request.args.get('cliente_id', type=int)
    query = Lote.query
    if cliente_id:
        query = query.filter_by(cliente_id=cliente_id)
    lotes = query.order_by(Lote.id.desc()).all()
    clientes = Cliente.query.order_by(Cliente.razon_social.asc()).all()
    return render_template('lotes/listar.html', lotes=lotes, clientes=clientes, cliente_filtro=cliente_id)


@bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    form = LoteForm()
    _cargar_choices_cliente(form)
    if form.validate_on_submit():
        lote = Lote()
        form.populate_obj(lote)
        db.session.add(lote)
        db.session.commit()
        flash('Lote agregado exitosamente.', 'success')
        return redirect(url_for('lotes.listar'))
    return render_template('lotes/form.html', form=form, titulo='Nuevo Lote')


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    lote = Lote.query.get_or_404(id)
    form = LoteForm(obj=lote)
    _cargar_choices_cliente(form)
    if form.validate_on_submit():
        form.populate_obj(lote)
        db.session.commit()
        flash('Lote actualizado correctamente.', 'success')
        return redirect(url_for('lotes.listar'))
    return render_template('lotes/form.html', form=form, titulo='Editar Lote')


@bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    lote = Lote.query.get_or_404(id)
    try:
        db.session.delete(lote)
        db.session.commit()
        flash('Lote eliminado correctamente.', 'warning')
    except IntegrityError:
        db.session.rollback()
        flash('No se puede eliminar: el lote tiene recetas asociadas.', 'danger')
    return redirect(url_for('lotes.listar'))


@bp.route('/<int:id>/identificar', methods=['GET', 'POST'])
@login_required
def identificar(id):
    lote = Lote.query.get_or_404(id)
    form = IdentificarPlantaForm()
    resultado = None

    if form.validate_on_submit():
        try:
            resultado = identificar_planta(form.imagen.data, form.organo.data)
            if not resultado['resultados']:
                flash('No se pudo identificar ninguna especie en la imagen.', 'warning')
        except IdentificacionError as exc:
            flash(str(exc), 'danger')

    return render_template('lotes/identificar.html', form=form, lote=lote, resultado=resultado)


@bp.route('/por_cliente/<int:cliente_id>')
@login_required
def por_cliente(cliente_id):
    """Devuelve los lotes activos de un cliente en JSON, para el combo dinámico del form de recetas."""
    lotes = Lote.query.filter_by(cliente_id=cliente_id, activo=True).order_by(Lote.nombre.asc()).all()
    return {
        'lotes': [{'id': l.id, 'nombre': l.nombre, 'cultivo': l.cultivo or ''} for l in lotes]
    }
