from datetime import datetime

from sqlalchemy import func

from app.extensions import db
from app.models import Receta, Cliente


def obtener_indicadores():
    """KPIs propios del sistema (sin dependencias externas)."""
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    hectareas_mes = (
        db.session.query(func.coalesce(func.sum(Receta.hectareas), 0.0))
        .filter(Receta.fecha >= inicio_mes)
        .scalar()
    )
    recetas_mes = (
        db.session.query(func.count(Receta.id))
        .filter(Receta.fecha >= inicio_mes)
        .scalar()
    )

    top_clientes = (
        db.session.query(
            Cliente.razon_social,
            func.sum(Receta.hectareas).label('total_ha'),
        )
        .join(Receta, Receta.cliente_id == Cliente.id)
        .group_by(Cliente.id)
        .order_by(func.sum(Receta.hectareas).desc())
        .limit(5)
        .all()
    )

    return {
        'hectareas_mes': hectareas_mes or 0.0,
        'recetas_mes': recetas_mes or 0,
        'top_clientes': [{'nombre': nombre, 'hectareas': total} for nombre, total in top_clientes],
    }
