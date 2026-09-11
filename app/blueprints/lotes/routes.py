import json

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.blueprints.lotes import bp
from app.blueprints.lotes.forms import LoteForm, IdentificarPlantaForm
from app.decorators import tiene_permiso_modulo
from app.models import Lote, Cliente
from app.services.plantnet import identificar_planta, IdentificacionError
from app.services.agromonitoring import guardar_poligono, obtener_ndvi, AgromonitoringError


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


@bp.route('/<int:id>/ndvi', methods=['GET', 'POST'])
@login_required
def ndvi(id):
    lote = Lote.query.get_or_404(id)

    if request.method == 'POST':
        coords_raw = request.form.get('coordenadas')
        if not coords_raw:
            flash('Dibujá el contorno del lote en el mapa antes de guardar.', 'danger')
        else:
            try:
                coordenadas = json.loads(coords_raw)
                guardar_poligono(lote, coordenadas)
                db.session.commit()
                flash('Polígono guardado correctamente.', 'success')
            except AgromonitoringError as exc:
                flash(str(exc), 'danger')
            except (ValueError, TypeError):
                flash('El contorno dibujado no es válido.', 'danger')
        return redirect(url_for('lotes.ndvi', id=id))

    centro = None
    if lote.latitud and lote.longitud:
        try:
            centro = [float(lote.latitud), float(lote.longitud)]
        except ValueError:
            centro = None
    if not centro:
        centro = [current_app.config['WEATHER_LAT'], current_app.config['WEATHER_LON']]

    poligono = json.loads(lote.poligono) if lote.poligono else None

    return render_template('lotes/ndvi.html', lote=lote, centro=centro, poligono=poligono, resultado=None)


@bp.route('/<int:id>/ndvi/consultar', methods=['POST'])
@login_required
def ndvi_consultar(id):
    lote = Lote.query.get_or_404(id)
    resultado = None

    if not lote.agromonitoring_id:
        flash('Primero guardá el polígono del lote.', 'warning')
        return redirect(url_for('lotes.ndvi', id=id))

    try:
        resultado = obtener_ndvi(lote.agromonitoring_id)
    except AgromonitoringError as exc:
        flash(str(exc), 'warning')

    centro = [float(lote.latitud), float(lote.longitud)] if lote.latitud and lote.longitud else \
        [current_app.config['WEATHER_LAT'], current_app.config['WEATHER_LON']]
    poligono = json.loads(lote.poligono) if lote.poligono else None

    return render_template('lotes/ndvi.html', lote=lote, centro=centro, poligono=poligono, resultado=resultado)


@bp.route('/por_cliente/<int:cliente_id>')
@login_required
def por_cliente(cliente_id):
    """Devuelve los lotes activos de un cliente en JSON, para el combo dinámico del form de recetas."""
    lotes = Lote.query.filter_by(cliente_id=cliente_id, activo=True).order_by(Lote.nombre.asc()).all()
    return {
        'lotes': [{'id': l.id, 'nombre': l.nombre} for l in lotes]
    }
