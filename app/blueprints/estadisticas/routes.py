import io

import pandas as pd
from flask import render_template, request, send_file, redirect, url_for, flash
from flask_login import login_required, current_user

from app.blueprints.estadisticas import bp
from app.blueprints.estadisticas.services import obtener_estadisticas
from app.decorators import tiene_permiso_modulo
from app.models import Cliente, Campania, PrincipioActivo, Usuario


@bp.before_request
def _verificar_permiso():
    if not current_user.is_authenticated:
        return None
    if not tiene_permiso_modulo('puede_recetas'):
        flash('No tenés permiso para acceder a Estadísticas.', 'danger')
        return redirect(url_for('dashboard'))


def _cargar_listas_filtro():
    return {
        'lista_clientes': Cliente.query.order_by(Cliente.razon_social.asc()).all(),
        'lista_campanias': Campania.query.order_by(Campania.nombre.desc(), Campania.cultivo.asc()).all(),
        'lista_principios': [p.nombre for p in PrincipioActivo.query.order_by(PrincipioActivo.nombre.asc()).all()],
        'lista_usuarios': Usuario.query.order_by(Usuario.usuario.asc()).all(),
    }


@bp.route('/')
@login_required
def index():
    datos = obtener_estadisticas(request.args)
    return render_template('estadisticas/index.html', datos=datos, **_cargar_listas_filtro())


@bp.route('/exportar_excel')
@login_required
def exportar_excel():
    datos = obtener_estadisticas(request.args)

    resumen = pd.DataFrame([{
        'Hectáreas tratadas': datos['hectareas_total'],
        'Recetas cargadas': datos['recetas_total'],
        'Costo total': datos['costo_total'],
        'Costo por hectárea': datos['costo_por_ha'],
    }])
    evolucion = pd.DataFrame({
        'Mes': datos['evolucion_mensual']['meses'],
        'Hectáreas': datos['evolucion_mensual']['hectareas'],
        'Costo': datos['evolucion_mensual']['costos'],
    })
    productos = pd.DataFrame(datos['top_productos']).rename(
        columns={'nombre': 'Producto', 'veces': 'Veces Recetado', 'cantidad': 'Cantidad Total'}
    )
    tipo_insumo = pd.DataFrame(datos['por_tipo_insumo']).rename(
        columns={'tipo': 'Tipo de Insumo', 'costo': 'Costo Total'}
    )
    principios = pd.DataFrame(datos['top_principios']).rename(
        columns={'nombre': 'Principio Activo', 'veces': 'Veces Recetado'}
    )
    clientes = pd.DataFrame(datos['top_clientes']).rename(
        columns={'nombre': 'Cliente', 'hectareas': 'Hectáreas Tratadas'}
    )
    campanias = pd.DataFrame(datos['top_campanias']).rename(
        columns={'nombre': 'Campaña', 'hectareas': 'Hectáreas Tratadas'}
    )
    ingenieros = pd.DataFrame(datos['top_ingenieros']).rename(
        columns={'nombre': 'Ingeniero', 'recetas': 'Recetas Cargadas', 'hectareas': 'Hectáreas Tratadas'}
    )

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        resumen.to_excel(writer, index=False, sheet_name='Resumen')
        evolucion.to_excel(writer, index=False, sheet_name='Evolucion Mensual')
        productos.to_excel(writer, index=False, sheet_name='Top Productos')
        tipo_insumo.to_excel(writer, index=False, sheet_name='Por Tipo de Insumo')
        principios.to_excel(writer, index=False, sheet_name='Top Principios Activos')
        clientes.to_excel(writer, index=False, sheet_name='Top Clientes')
        campanias.to_excel(writer, index=False, sheet_name='Top Campanias')
        ingenieros.to_excel(writer, index=False, sheet_name='Recetas por Ingeniero')
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='estadisticas_recetas.xlsx',
    )
