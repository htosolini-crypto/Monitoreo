import requests
from flask import current_app

from app.utils import cache_temporal

WMO_DESCRIPCIONES = {
    0: ('Despejado', 'fa-sun'),
    1: ('Mayormente despejado', 'fa-cloud-sun'),
    2: ('Parcialmente nublado', 'fa-cloud-sun'),
    3: ('Nublado', 'fa-cloud'),
    45: ('Niebla', 'fa-smog'),
    48: ('Niebla escarchada', 'fa-smog'),
    51: ('Llovizna débil', 'fa-cloud-rain'),
    53: ('Llovizna', 'fa-cloud-rain'),
    55: ('Llovizna intensa', 'fa-cloud-rain'),
    61: ('Lluvia débil', 'fa-cloud-showers-heavy'),
    63: ('Lluvia', 'fa-cloud-showers-heavy'),
    65: ('Lluvia intensa', 'fa-cloud-showers-heavy'),
    71: ('Nevada débil', 'fa-snowflake'),
    73: ('Nevada', 'fa-snowflake'),
    75: ('Nevada intensa', 'fa-snowflake'),
    80: ('Chubascos débiles', 'fa-cloud-showers-heavy'),
    81: ('Chubascos', 'fa-cloud-showers-heavy'),
    82: ('Chubascos intensos', 'fa-cloud-showers-heavy'),
    95: ('Tormenta', 'fa-bolt'),
    96: ('Tormenta con granizo', 'fa-cloud-bolt'),
    99: ('Tormenta con granizo', 'fa-cloud-bolt'),
}


def _descripcion(codigo):
    return WMO_DESCRIPCIONES.get(codigo, ('-', 'fa-cloud'))


@cache_temporal(ttl_segundos=1200)
def obtener_clima():
    """Consulta Open-Meteo (gratis, sin API key) para la ubicación configurada.
    Devuelve None si el servicio no está disponible, para no romper el dashboard."""
    lat = current_app.config.get('WEATHER_LAT')
    lon = current_app.config.get('WEATHER_LON')
    etiqueta = current_app.config.get('WEATHER_LABEL', 'Ubicación')

    if lat is None or lon is None:
        return None

    try:
        response = requests.get(
            'https://api.open-meteo.com/v1/forecast',
            params={
                'latitude': lat,
                'longitude': lon,
                'current': 'temperature_2m,wind_speed_10m,precipitation,weather_code',
                'daily': 'precipitation_probability_max,temperature_2m_max,temperature_2m_min,weather_code',
                'timezone': 'America/Argentina/Buenos_Aires',
                'forecast_days': 4,
            },
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None

    actual = data.get('current', {})
    diario = data.get('daily', {})
    desc_actual, icono_actual = _descripcion(actual.get('weather_code'))

    pronostico = []
    fechas = diario.get('time', [])
    for i, fecha in enumerate(fechas[1:4], start=1):
        desc, icono = _descripcion(diario.get('weather_code', [None] * len(fechas))[i])
        pronostico.append({
            'fecha': fecha,
            'temp_max': diario.get('temperature_2m_max', [None] * len(fechas))[i],
            'temp_min': diario.get('temperature_2m_min', [None] * len(fechas))[i],
            'prob_lluvia': diario.get('precipitation_probability_max', [None] * len(fechas))[i],
            'descripcion': desc,
            'icono': icono,
        })

    return {
        'etiqueta': etiqueta,
        'temperatura': actual.get('temperature_2m'),
        'viento': actual.get('wind_speed_10m'),
        'precipitacion': actual.get('precipitation'),
        'descripcion': desc_actual,
        'icono': icono_actual,
        'pronostico': pronostico,
    }
