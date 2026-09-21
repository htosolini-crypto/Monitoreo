from flask import render_template, redirect, url_for, flash, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.blueprints.parametros import bp
from app.blueprints.parametros.forms import ParametroForm
from app.decorators import admin_required
from app.models import Parametro


def _categorias_existentes():
    filas = db.session.query(Parametro.categoria).distinct().order_by(Parametro.categoria.asc()).all()
    return [f[0] for f in filas]


def _cargar_choices(form):
    form.categoria_existente.choices = [('', '-- Seleccionar --')] + [
        (c, c) for c in _categorias_existentes()
    ]


def _resolver_categoria(form):
    return (form.categoria_nueva.data or '').strip() or form.categoria_existente.data


@bp.route('/')
@admin_required
def listar():
    categoria_filtro = request.args.get('categoria', '')
    query = Parametro.query
    if categoria_filtro:
        query = query.filter_by(categoria=categoria_filtro)
    parametros = query.order_by(Parametro.categoria.asc(), Parametro.orden.asc(), Parametro.id.asc()).all()
    return render_template(
        'parametros/listar.html',
        parametros=parametros,
        categorias=_categorias_existentes(),
        categoria_filtro=categoria_filtro,
    )


@bp.route('/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo():
    form = ParametroForm()
    _cargar_choices(form)

    if form.validate_on_submit():
        categoria = _resolver_categoria(form)
        if not categoria:
            flash('Debés indicar una categoría, existente o nueva.', 'danger')
        else:
            parametro = Parametro(
                categoria=categoria,
                valor=form.valor.data,
                abreviatura=form.abreviatura.data,
                orden=form.orden.data or 0,
                activo=form.activo.data,
            )
            db.session.add(parametro)
            try:
                db.session.commit()
                flash('Parámetro creado correctamente.', 'success')
                return redirect(url_for('parametros.listar', categoria=categoria))
            except IntegrityError:
                db.session.rollback()
                flash('Ya existe un parámetro con esa categoría y valor.', 'danger')

    return render_template('parametros/form.html', form=form, titulo='Nuevo Parámetro')


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar(id):
    parametro = Parametro.query.get_or_404(id)
    form = ParametroForm(obj=parametro)
    _cargar_choices(form)
    if request.method == 'GET':
        form.categoria_existente.data = parametro.categoria

    if form.validate_on_submit():
        categoria = _resolver_categoria(form)
        if not categoria:
            flash('Debés indicar una categoría, existente o nueva.', 'danger')
        else:
            parametro.categoria = categoria
            parametro.valor = form.valor.data
            parametro.abreviatura = form.abreviatura.data
            parametro.orden = form.orden.data or 0
            parametro.activo = form.activo.data
            try:
                db.session.commit()
                flash('Parámetro actualizado correctamente.', 'success')
                return redirect(url_for('parametros.listar', categoria=categoria))
            except IntegrityError:
                db.session.rollback()
                flash('Ya existe un parámetro con esa categoría y valor.', 'danger')

    return render_template('parametros/form.html', form=form, titulo='Editar Parámetro')


@bp.route('/<int:id>/eliminar', methods=['POST'])
@admin_required
def eliminar(id):
    parametro = Parametro.query.get_or_404(id)
    categoria = parametro.categoria
    db.session.delete(parametro)
    db.session.commit()
    flash('Parámetro eliminado correctamente.', 'warning')
    return redirect(url_for('parametros.listar', categoria=categoria))
