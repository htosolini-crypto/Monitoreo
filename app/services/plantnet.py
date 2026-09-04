import requests
from flask import current_app

PLANTNET_URL = 'https://my-api.plantnet.org/v2/identify/all'
SCORE_MINIMO = 5.0  # % de confianza; por debajo de esto la API devuelve coincidencias sin valor real


class IdentificacionError(Exception):
    pass


def identificar_planta(archivo, organo='auto'):
    """Envía una foto a Pl@ntNet (gratis, con API key propia) para identificar la especie.
    `archivo` es un FileStorage de Flask-WTF. Devuelve una lista de resultados."""
    api_key = current_app.config.get('PLANTNET_API_KEY')
    if not api_key:
        raise IdentificacionError(
            'La identificación de plantas no está configurada. Definí PLANTNET_API_KEY en el archivo .env.'
        )

    try:
        response = requests.post(
            PLANTNET_URL,
            params={'api-key': api_key},
            data={'organs': organo},
            files={'images': (archivo.filename, archivo.stream, archivo.mimetype)},
            timeout=15,
        )
    except requests.RequestException as exc:
        raise IdentificacionError(f'No se pudo conectar con el servicio de identificación: {exc}')

    if response.status_code == 401:
        raise IdentificacionError('La API Key de Pl@ntNet es inválida.')
    if response.status_code == 429:
        raise IdentificacionError('Se alcanzó el límite de identificaciones del plan gratuito por hoy.')
    if not response.ok:
        raise IdentificacionError(f'El servicio de identificación respondió con un error ({response.status_code}).')

    data = response.json()
    resultados = []
    for item in data.get('results', [])[:5]:
        score = round((item.get('score') or 0) * 100, 1)
        if score < SCORE_MINIMO:
            continue
        especie = item.get('species', {})
        resultados.append({
            'score': score,
            'nombre_cientifico': especie.get('scientificNameWithoutAuthor'),
            'nombres_comunes': especie.get('commonNames', []),
            'familia': (especie.get('family') or {}).get('scientificNameWithoutAuthor'),
        })

    return {
        'resultados': resultados,
        'restantes_hoy': data.get('remainingIdentificationRequests'),
    }
