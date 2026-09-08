from sqlalchemy import func

from app.extensions import db
from app.models import Receta, RecetaDetalle, Producto, Cliente


def _leer_filtros(args):
    return {
        'fecha_desde': (args.get('fecha_desde') or '').strip(),
        'fecha_hasta': (args.get('fecha_hasta') or '').strip(),
        'cliente_id': args.get('cliente_id', '').strip() if args.get('cliente_id') else '',
    }


def _filtrar_recetas(query, filtros):
    if filtros['fecha_desde']:
        query = query.filter(func.date(Receta.fecha) >= filtros['fecha_desde'])
    if filtros['fecha_hasta']:
        query = query.filter(func.date(Receta.fecha) <= filtros['fecha_hasta'])
    if filtros['cliente_id']:
        query = query.filter(Receta.cliente_id == filtros['cliente_id'])
    return query


def obtener_estadisticas(args):
    filtros = _leer_filtros(args)

    # --- KPIs e hectáreas: sobre Receta sola, sin join a detalle (evita fan-out) ---
    q_recetas = _filtrar_recetas(Receta.query, filtros)
    hectareas_total = q_recetas.with_entities(func.coalesce(func.sum(Receta.hectareas), 0.0)).scalar()
    recetas_total = q_recetas.with_entities(func.count(Receta.id)).scalar()

    # --- Costo total: join a detalle, solo para sumar importe (no duplica hectáreas) ---
    q_costo = _filtrar_recetas(
        db.session.query(func.coalesce(func.sum(RecetaDetalle.importe_total), 0.0))
        .join(Receta, RecetaDetalle.receta_id == Receta.id),
        filtros,
    )
    costo_total = q_costo.scalar()
    costo_por_ha = round(costo_total / hectareas_total, 2) if hectareas_total else 0.0

    # --- Evolución mensual: hectáreas (sobre Receta) y costo (join a detalle), por separado ---
    mes = func.to_char(func.date_trunc('month', Receta.fecha), 'YYYY-MM')

    filas_ha = (
        _filtrar_recetas(
            db.session.query(mes.label('mes'), func.sum(Receta.hectareas).label('hectareas')),
            filtros,
        )
        .group_by('mes')
        .all()
    )
    filas_costo = (
        _filtrar_recetas(
            db.session.query(mes.label('mes'), func.sum(RecetaDetalle.importe_total).label('costo'))
            .join(RecetaDetalle, RecetaDetalle.receta_id == Receta.id),
            filtros,
        )
        .group_by('mes')
        .all()
    )
    ha_por_mes = {f.mes: f.hectareas for f in filas_ha}
    costo_por_mes = {f.mes: f.costo for f in filas_costo}
    meses = sorted(set(ha_por_mes) | set(costo_por_mes))
    evolucion_mensual = {
        'meses': meses,
        'hectareas': [round(ha_por_mes.get(m, 0.0), 2) for m in meses],
        'costos': [round(costo_por_mes.get(m, 0.0), 2) for m in meses],
    }

    # --- Top productos más recetados ---
    filas = (
        _filtrar_recetas(
            db.session.query(
                Producto.denominacion_comercial,
                func.count(RecetaDetalle.id).label('veces'),
                func.sum(RecetaDetalle.cantidad_total).label('cantidad'),
            )
            .join(RecetaDetalle, RecetaDetalle.producto_id == Producto.id)
            .join(Receta, RecetaDetalle.receta_id == Receta.id),
            filtros,
        )
        .group_by(Producto.id, Producto.denominacion_comercial)
        .order_by(func.count(RecetaDetalle.id).desc())
        .limit(10)
        .all()
    )
    top_productos = [
        {'nombre': f.denominacion_comercial, 'veces': f.veces, 'cantidad': round(f.cantidad or 0, 2)}
        for f in filas
    ]

    # --- Distribución por tipo de insumo (costo total) ---
    filas = (
        _filtrar_recetas(
            db.session.query(
                func.coalesce(Producto.id_insumo, 'Sin clasificar').label('tipo'),
                func.sum(RecetaDetalle.importe_total).label('costo'),
            )
            .join(RecetaDetalle, RecetaDetalle.producto_id == Producto.id)
            .join(Receta, RecetaDetalle.receta_id == Receta.id),
            filtros,
        )
        .group_by('tipo')
        .order_by(func.sum(RecetaDetalle.importe_total).desc())
        .all()
    )
    por_tipo_insumo = [{'tipo': f.tipo, 'costo': round(f.costo or 0, 2)} for f in filas]

    # --- Top principios activos ---
    filas = (
        _filtrar_recetas(
            db.session.query(
                Producto.principio_activo,
                func.count(RecetaDetalle.id).label('veces'),
            )
            .join(RecetaDetalle, RecetaDetalle.producto_id == Producto.id)
            .join(Receta, RecetaDetalle.receta_id == Receta.id),
            filtros,
        )
        .group_by(Producto.principio_activo)
        .order_by(func.count(RecetaDetalle.id).desc())
        .limit(10)
        .all()
    )
    top_principios = [{'nombre': f.principio_activo, 'veces': f.veces} for f in filas]

    # --- Top clientes por hectáreas (sobre Receta+Cliente, sin join a detalle) ---
    filas = (
        _filtrar_recetas(
            db.session.query(
                Cliente.razon_social,
                func.sum(Receta.hectareas).label('hectareas'),
            )
            .join(Receta, Receta.cliente_id == Cliente.id),
            filtros,
        )
        .group_by(Cliente.id, Cliente.razon_social)
        .order_by(func.sum(Receta.hectareas).desc())
        .limit(10)
        .all()
    )
    top_clientes = [{'nombre': f.razon_social, 'hectareas': round(f.hectareas or 0, 2)} for f in filas]

    return {
        'filtros': filtros,
        'hectareas_total': round(hectareas_total or 0, 2),
        'recetas_total': recetas_total or 0,
        'costo_total': round(costo_total or 0, 2),
        'costo_por_ha': costo_por_ha,
        'evolucion_mensual': evolucion_mensual,
        'top_productos': top_productos,
        'por_tipo_insumo': por_tipo_insumo,
        'top_principios': top_principios,
        'top_clientes': top_clientes,
    }
