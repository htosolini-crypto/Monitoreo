from sqlalchemy import or_, func, cast, Integer

from app.models import Receta, Cliente, Lote, RecetaDetalle, Producto, PrincipioActivo


def obtener_recetas_filtradas(args):
    q = (args.get('q') or '').strip()
    fecha_desde = (args.get('fecha_desde') or '').strip()
    fecha_hasta = (args.get('fecha_hasta') or '').strip()
    cliente_filtro = args.get('cliente_id', '')
    principio_activo_filtro = args.get('principio_activo', '')
    receta_desde = (args.get('receta_desde') or '').strip()
    receta_hasta = (args.get('receta_hasta') or '').strip()

    query = (
        Receta.query
        .join(Cliente, Receta.cliente_id == Cliente.id)
        .join(Lote, Receta.lote_id == Lote.id)
        .outerjoin(RecetaDetalle, RecetaDetalle.receta_id == Receta.id)
        .outerjoin(Producto, RecetaDetalle.producto_id == Producto.id)
        .outerjoin(PrincipioActivo, Producto.principio_activo_id == PrincipioActivo.id)
    )

    if q:
        term = f"%{q}%"
        query = query.filter(or_(Lote.nombre.ilike(term), Producto.denominacion_comercial.ilike(term)))

    if fecha_desde:
        query = query.filter(func.date(Receta.fecha) >= fecha_desde)

    if fecha_hasta:
        query = query.filter(func.date(Receta.fecha) <= fecha_hasta)

    if cliente_filtro:
        query = query.filter(Receta.cliente_id == cliente_filtro)

    if principio_activo_filtro:
        query = query.filter(PrincipioActivo.nombre == principio_activo_filtro)

    if receta_desde:
        query = query.filter(
            cast(func.substr(Receta.numero_receta, 6), Integer) >= cast(func.substr(receta_desde, 6), Integer)
        )

    if receta_hasta:
        query = query.filter(
            cast(func.substr(Receta.numero_receta, 6), Integer) <= cast(func.substr(receta_hasta, 6), Integer)
        )

    recetas = query.distinct().order_by(Receta.id.desc()).all()

    filtros = {
        'q': q,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'cliente_filtro': cliente_filtro,
        'principio_activo_filtro': principio_activo_filtro,
        'receta_desde': receta_desde,
        'receta_hasta': receta_hasta,
    }
    return recetas, filtros
