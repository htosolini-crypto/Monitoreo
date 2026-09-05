from datetime import datetime, timedelta

import requests
from flask import current_app

BASE_URL = 'http://api.agromonitoring.com/agro/1.0'
DIAS_BUSQUEDA_NDVI = 60


class AgromonitoringError(Exception):
    pass


def _api_key():
    api_key = current_app.config.get('AGROMONITORING_API_KEY')
    if not api_key:
        raise AgromonitoringError(
            'El NDVI no está configurado. Definí AGROMONITORING_API_KEY en el archivo .env.'
        )
    return api_key


def _cerrar_anillo(coordenadas):
    """Asegura que el primer y último punto del polígono sean idénticos, como exige GeoJSON."""
    if coordenadas and coordenadas[0] != coordenadas[-1]:
        coordenadas = coordenadas + [coordenadas[0]]
    return coordenadas


def guardar_poligono(lote, coordenadas):
    """Registra (o reemplaza) el polígono de un lote en Agromonitoring.
    `coordenadas` es una lista de pares [lng, lat]. Actualiza el propio `lote` in-place."""
    api_key = _api_key()
    coordenadas = _cerrar_anillo(coordenadas)

    if lote.agromonitoring_id:
        try:
            requests.delete(
                f'{BASE_URL}/polygons/{lote.agromonitoring_id}',
                params={'appid': api_key},
                timeout=10,
            )
        except requests.RequestException:
            pass  # best-effort: si falla el borrado, igual creamos el nuevo

    try:
        response = requests.post(
            f'{BASE_URL}/polygons',
            params={'appid': api_key},
            json={
                'name': lote.nombre,
                'geo_json': {
                    'type': 'Feature',
                    'properties': {},
                    'geometry': {'type': 'Polygon', 'coordinates': [coordenadas]},
                },
            },
            timeout=15,
        )
    except requests.RequestException as exc:
        raise AgromonitoringError(f'No se pudo conectar con Agromonitoring: {exc}')

    if not response.ok:
        mensaje = response.text
        try:
            mensaje = response.json().get('message', mensaje)
        except ValueError:
            pass
        raise AgromonitoringError(f'Agromonitoring rechazó el polígono: {mensaje}')

    data = response.json()
    lote.agromonitoring_id = data.get('id')
    lote.poligono = coordenadas


def obtener_ndvi(polygon_id):
    """Busca la imagen NDVI más reciente (sin nubes, límite del plan gratuito) para el polígono."""
    api_key = _api_key()
    ahora = datetime.utcnow()
    desde = ahora - timedelta(days=DIAS_BUSQUEDA_NDVI)

    try:
        response = requests.get(
            f'{BASE_URL}/image/search',
            params={
                'start': int(desde.timestamp()),
                'end': int(ahora.timestamp()),
                'polyid': polygon_id,
                'appid': api_key,
            },
            timeout=15,
        )
    except requests.RequestException as exc:
        raise AgromonitoringError(f'No se pudo conectar con Agromonitoring: {exc}')

    if not response.ok:
        raise AgromonitoringError(f'Agromonitoring respondió con un error ({response.status_code}).')

    escenas = [e for e in response.json() if e.get('stats', {}).get('ndvi')]
    if not escenas:
        raise AgromonitoringError(
            f'No hay imágenes NDVI libres de nubes en los últimos {DIAS_BUSQUEDA_NDVI} días '
            '(el plan gratuito solo admite escenas con 0% de nubosidad).'
        )

    escena = max(escenas, key=lambda e: e.get('dt', 0))

    try:
        stats_response = requests.get(escena['stats']['ndvi'], timeout=15)
        stats_response.raise_for_status()
        stats = stats_response.json()
    except (requests.RequestException, ValueError) as exc:
        raise AgromonitoringError(f'No se pudieron obtener las estadísticas NDVI: {exc}')

    return {
        'fecha': datetime.utcfromtimestamp(escena['dt']),
        'mean': stats.get('mean'),
        'min': stats.get('min'),
        'max': stats.get('max'),
        'imagen_url': escena.get('image', {}).get('ndvi'),
    }
