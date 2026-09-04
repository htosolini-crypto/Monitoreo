import re
import time
from functools import wraps


def cache_temporal(ttl_segundos):
    """Cachea en memoria el resultado de una función sin argumentos por un tiempo limitado.
    Evita golpear una API externa en cada carga del dashboard."""
    def decorador(func):
        estado = {'valor': None, 'expira': 0}

        @wraps(func)
        def wrapper():
            ahora = time.monotonic()
            if estado['valor'] is None or ahora >= estado['expira']:
                estado['valor'] = func()
                estado['expira'] = ahora + ttl_segundos
            return estado['valor']

        return wrapper
    return decorador


def validar_cuit(cuit):
    """Valida el dígito verificador de un CUIT/CUIL argentino (algoritmo módulo 11)."""
    digitos = re.sub(r'\D', '', cuit or '')
    if len(digitos) != 11:
        return False

    multiplicadores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    total = sum(int(digitos[i]) * multiplicadores[i] for i in range(10))
    resto = total % 11
    verificador = 11 - resto

    if verificador == 11:
        verificador = 0
    elif verificador == 10:
        if digitos[:2] == '23':
            verificador = 9
        else:
            return False

    return verificador == int(digitos[10])
