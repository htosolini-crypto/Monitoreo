from app.models.parametro import Parametro

# Unidad base (valor en Parámetros, categoría unidad_producto) -> (unidad mayor, factor).
# Al llegar a un factor de la unidad base, la cantidad se muestra en la unidad mayor.
CONVERSIONES = {
    'Centimetros 3': ('Litros', 1000),
    'Gramos': ('Kilogramos', 1000),
}


def abreviaturas():
    return {
        p.valor: (p.abreviatura or p.valor)
        for p in Parametro.query.filter_by(categoria='unidad_producto').all()
    }


def conversiones_para_formulario():
    """{unidad base: {'abrev': abreviatura de la unidad mayor, 'factor': n}} para el JS de la receta."""
    abrev = abreviaturas()
    return {
        base: {'abrev': abrev.get(mayor, mayor), 'factor': factor}
        for base, (mayor, factor) in CONVERSIONES.items()
    }


def unidad_legible(cantidad, unidad):
    """Devuelve (abreviatura, factor): la unidad mayor y su factor si la cantidad llega a 1000, si no la base y 1."""
    abrev = abreviaturas()
    if unidad in CONVERSIONES:
        mayor, factor = CONVERSIONES[unidad]
        if abs(cantidad) >= factor:
            return abrev.get(mayor, mayor), factor
    return abrev.get(unidad, unidad), 1


def cantidad_legible(cantidad, unidad):
    """Devuelve (cantidad, abreviatura) llevando cm3 a litros y gramos a kilos desde 1000 en adelante."""
    abreviatura, factor = unidad_legible(cantidad, unidad)
    return cantidad / factor, abreviatura
