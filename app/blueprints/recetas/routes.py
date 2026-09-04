import io
from datetime import datetime

from flask import render_template, redirect, url_for, flash, request, send_file, make_response
from flask_login import login_required, current_user
import pandas as pd

try:
    from xhtml2pdf import pisa
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

from app.extensions import db, mail
from app.blueprints.recetas import bp
from app.blueprints.recetas.forms import RecetaForm
from app.blueprints.recetas.services import obtener_recetas_filtradas
from app.decorators import tiene_permiso_modulo
from app.models import Receta, RecetaDetalle, Cliente, Lote, Producto
from flask_mail import Message


@bp.before_request
def _verificar_permiso():
    if not current_user.is_authenticated:
        return None
    if not tiene_permiso_modulo('puede_recetas'):
        flash('No tenés permiso para acceder a Recetas.', 'danger')
        return redirect(url_for('dashboard'))


def _cargar_choices(form, cliente_id=None):
    clientes = Cliente.query.order_by(Cliente.razon_social.asc()).all()
    form.cliente_id.choices = [(c.id, c.razon_social) for c in clientes]

    lotes_query = Lote.query.order_by(Lote.nombre.asc())
    if cliente_id:
        lotes_query = lotes_query.filter_by(cliente_id=cliente_id)
    form.lote_id.choices = [(l.id, l.nombre) for l in lotes_query.all()]


def _construir_detalle(receta_id, producto_id, dosis_val, hectareas):
    producto = Producto.query.get(int(producto_id))
    dosis = float(dosis_val or 0.0)
    cantidad_total = round(dosis * hectareas, 2)
    precio_unitario = producto.precio if producto else 0.0
    importe_total = round(cantidad_total * precio_unitario, 2)
    return RecetaDetalle(
        receta_id=receta_id,
        producto_id=int(producto_id),
        dosis=dosis,
        cantidad_total=cantidad_total,
        precio_unitario=precio_unitario,
        importe_total=importe_total,
    )


@bp.route('/')
@login_required
def listar():
    lista_clientes = Cliente.query.order_by(Cliente.razon_social.asc()).all()
    lista_principios = (
        db.session.query(Producto.principio_activo)
        .filter(Producto.principio_activo.isnot(None), Producto.principio_activo != '')
        .distinct()
        .order_by(Producto.principio_activo.asc())
        .all()
    )
    lista_principios = [p[0] for p in lista_principios]

    recetas, filtros = obtener_recetas_filtradas(request.args)

    return render_template(
        'recetas/listar.html',
        recetas=recetas,
        lista_clientes=lista_clientes,
        lista_principios=lista_principios,
        **filtros,
    )


@bp.route('/exportar_excel')
@login_required
def exportar_excel():
    recetas, _ = obtener_recetas_filtradas(request.args)

    filas = []
    for r in recetas:
        if r.detalles:
            for d in r.detalles:
                filas.append({
                    'N° Receta': r.numero_receta,
                    'Fecha': r.fecha,
                    'Cliente': r.cliente.razon_social,
                    'Lote': r.lote.nombre,
                    'Hectáreas': r.hectareas,
                    'Producto': d.producto.denominacion_comercial,
                    'Principio Activo': d.producto.principio_activo,
                    'Marca': d.producto.marca,
                    'Dosis': d.dosis,
                    'Unidad': d.producto.unidad,
                    'Cantidad Total': d.cantidad_total,
                    'Precio Unitario': d.precio_unitario,
                    'Importe Total': d.importe_total,
                    'Observaciones': r.observaciones,
                })
        else:
            filas.append({
                'N° Receta': r.numero_receta,
                'Fecha': r.fecha,
                'Cliente': r.cliente.razon_social,
                'Lote': r.lote.nombre,
                'Hectáreas': r.hectareas,
                'Producto': '-',
                'Principio Activo': '-',
                'Marca': '-',
                'Dosis': 0,
                'Unidad': '-',
                'Cantidad Total': 0,
                'Precio Unitario': 0,
                'Importe Total': 0,
                'Observaciones': r.observaciones,
            })

    df = pd.DataFrame(filas)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Recetas')
    output.seek(0)

    filename = f"reporte_recetas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename,
    )


@bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    form = RecetaForm()
    cliente_id = request.form.get('cliente_id', type=int) or request.args.get('cliente_id', type=int)
    _cargar_choices(form, cliente_id)

    if form.validate_on_submit():
        productos_ids = request.form.getlist('producto_id[]')
        dosis_lista = request.form.getlist('dosis[]')

        if not productos_ids:
            flash('Debes seleccionar al menos un producto.', 'danger')
            return render_template('recetas/form.html', form=form, titulo='Nueva Receta', productos=Producto.query.order_by(Producto.denominacion_comercial.asc()).all())

        receta = Receta(
            numero_receta=Receta.generar_numero(db.session),
            cliente_id=form.cliente_id.data,
            lote_id=form.lote_id.data,
            hectareas=form.hectareas.data,
            observaciones=form.observaciones.data,
        )
        db.session.add(receta)
        db.session.flush()

        for p_id, dosis_val in zip(productos_ids, dosis_lista):
            db.session.add(_construir_detalle(receta.id, p_id, dosis_val, form.hectareas.data))

        db.session.commit()
        flash(f'Receta {receta.numero_receta} creada con éxito.', 'success')
        return redirect(url_for('recetas.listar'))

    productos = Producto.query.order_by(Producto.denominacion_comercial.asc()).all()
    proximo_numero = Receta.generar_numero(db.session)
    return render_template('recetas/form.html', form=form, titulo='Nueva Receta', productos=productos, proximo_numero=proximo_numero)


@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    receta = Receta.query.get_or_404(id)
    form = RecetaForm(obj=receta)
    cliente_id = request.form.get('cliente_id', type=int) or receta.cliente_id
    _cargar_choices(form, cliente_id)

    if form.validate_on_submit():
        productos_ids = request.form.getlist('producto_id[]')
        dosis_lista = request.form.getlist('dosis[]')

        if not productos_ids:
            flash('Debes seleccionar al menos un producto.', 'danger')
            return redirect(url_for('recetas.editar', id=id))

        receta.cliente_id = form.cliente_id.data
        receta.lote_id = form.lote_id.data
        receta.hectareas = form.hectareas.data
        receta.observaciones = form.observaciones.data

        RecetaDetalle.query.filter_by(receta_id=id).delete()

        for p_id, dosis_val in zip(productos_ids, dosis_lista):
            db.session.add(_construir_detalle(id, p_id, dosis_val, form.hectareas.data))

        db.session.commit()
        flash('Receta actualizada correctamente.', 'success')
        return redirect(url_for('recetas.listar'))

    productos = Producto.query.order_by(Producto.denominacion_comercial.asc()).all()
    return render_template('recetas/form.html', form=form, titulo='Editar Receta', receta=receta, productos=productos)


@bp.route('/<int:id>')
@login_required
def ver(id):
    receta = Receta.query.get_or_404(id)
    return render_template('recetas/detalle.html', receta=receta)


@bp.route('/<int:id>/imprimir')
@login_required
def imprimir(id):
    receta = Receta.query.get_or_404(id)
    return render_template('recetas/pdf.html', receta=receta, auto_print=True)


@bp.route('/<int:id>/pdf')
@login_required
def descargar_pdf(id):
    receta = Receta.query.get_or_404(id)
    html = render_template('recetas/pdf.html', receta=receta, auto_print=False)

    if PDF_SUPPORT:
        buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(io.StringIO(html), dest=buffer)
        if not pisa_status.err:
            response = make_response(buffer.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename=Receta_{receta.numero_receta}.pdf'
            return response

    return html


@bp.route('/<int:id>/enviar_email')
@login_required
def enviar_email(id):
    receta = Receta.query.get_or_404(id)

    if not receta.cliente.email:
        flash('El cliente asociado a esta receta no tiene una dirección de email configurada.', 'warning')
        return redirect(url_for('recetas.ver', id=id))

    try:
        html_content = render_template('recetas/email.html', receta=receta)
        msg = Message(
            subject=f"Receta de Aplicación N° {receta.numero_receta}",
            recipients=[receta.cliente.email],
            html=html_content,
            charset='utf-8',
        )
        mail.send(msg)
        flash(f'Receta enviada exitosamente a {receta.cliente.email}.', 'success')
    except Exception as e:
        flash(f'Error al enviar el correo electrónico: {str(e)}', 'danger')

    return redirect(url_for('recetas.ver', id=id))


@bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    receta = Receta.query.get_or_404(id)
    db.session.delete(receta)
    db.session.commit()
    flash('Receta eliminada correctamente.', 'warning')
    return redirect(url_for('recetas.listar'))
