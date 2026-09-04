import requests

from app.utils import cache_temporal

CASAS_A_MOSTRAR = ['oficial', 'blue']


@cache_temporal(ttl_segundos=600)
def obtener_cotizaciones_dolar():
    """Consulta dolarapi.com (gratis, sin API key). Devuelve None si falla."""
    try:
        response = requests.get('https://dolarapi.com/v1/dolares', timeout=5)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None

    por_casa = {item.get('casa'): item for item in data}
    resultado = []
    for casa in CASAS_A_MOSTRAR:
        item = por_casa.get(casa)
        if item:
            resultado.append({
                'nombre': item.get('nombre'),
                'compra': item.get('compra'),
                'venta': item.get('venta'),
            })

    return resultado or None
