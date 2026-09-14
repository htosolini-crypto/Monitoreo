import re
from urllib.parse import urlparse

import requests

DOMINIOS_PERMITIDOS = ('google.com', 'goo.gl', 'g.co')

PATRONES_COORDENADAS = [
    re.compile(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)'),
    re.compile(r'/search/(-?\d+\.\d+),\+?(-?\d+\.\d+)'),
    re.compile(r'@(-?\d+\.\d+),(-?\d+\.\d+)'),
    re.compile(r'[?&]q=(-?\d+\.\d+),(-?\d+\.\d+)'),
]


class MapsError(Exception):
    pass


def extraer_coordenadas(enlace):
    """Sigue el enlace de Google Maps y extrae latitud/longitud de la URL final."""
    enlace = (enlace or '').strip()
    if not enlace:
        raise MapsError('El enlace de Google Maps está vacío.')

    parsed = urlparse(enlace)
    dominio = parsed.netloc.lower()
    if parsed.scheme not in ('http', 'https') or not any(
        dominio == d or dominio.endswith('.' + d) for d in DOMINIOS_PERMITIDOS
    ):
        raise MapsError('El enlace debe ser un enlace válido de Google Maps (google.com, goo.gl o g.co).')

    try:
        respuesta = requests.head(
            enlace, allow_redirects=True, timeout=6, headers={'User-Agent': 'Mozilla/5.0'}
        )
    except requests.RequestException:
        raise MapsError('No se pudo abrir el enlace de Google Maps para obtener las coordenadas.')

    url_final = respuesta.url
    for patron in PATRONES_COORDENADAS:
        match = patron.search(url_final)
        if match:
            return float(match.group(1)), float(match.group(2))

    raise MapsError(
        'No se pudieron extraer las coordenadas del enlace. Se guardó el enlace igualmente, '
        'pero el mapa de NDVI usará una ubicación por defecto.'
    )


def actualizar_coordenadas_desde_enlace(obj):
    """Actualiza obj.latitud/obj.longitud a partir de obj.enlace_maps. Devuelve un mensaje de advertencia o None."""
    if not obj.enlace_maps:
        obj.latitud = None
        obj.longitud = None
        return None

    try:
        lat, lng = extraer_coordenadas(obj.enlace_maps)
        obj.latitud = str(lat)
        obj.longitud = str(lng)
        return None
    except MapsError as exc:
        obj.latitud = None
        obj.longitud = None
        return str(exc)
