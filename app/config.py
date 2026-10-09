import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))


def _database_url():
    url = os.environ.get('DATABASE_URL')
    if not url:
        return 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'cultivos.db')
    # Algunos proveedores entregan "postgres://", esquema que SQLAlchemy 2 ya no acepta.
    if url.startswith('postgres://'):
        url = 'postgresql://' + url[len('postgres://'):]
    return url


def _bool(nombre, default='false'):
    return os.environ.get(nombre, default).strip().lower() in ('1', 'true', 'yes', 'si')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # En producción (HTTPS) definir SESSION_COOKIE_SECURE=true para que las cookies solo viajen cifradas.
    SESSION_COOKIE_SECURE = _bool('SESSION_COOKIE_SECURE')
    REMEMBER_COOKIE_SECURE = _bool('SESSION_COOKIE_SECURE')
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SAMESITE = 'Lax'

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = (
        os.environ.get('MAIL_DEFAULT_SENDER_NAME', 'Sistema de Gestión y Monitoreo Agronómico'),
        os.environ.get('MAIL_DEFAULT_SENDER_EMAIL', os.environ.get('MAIL_USERNAME')),
    )
    MAIL_ASCII_ATTACHMENTS = False

    WEATHER_LAT = float(os.environ.get('WEATHER_LAT', '-30.3614'))
    WEATHER_LON = float(os.environ.get('WEATHER_LON', '-61.9156'))
    WEATHER_LABEL = os.environ.get('WEATHER_LABEL', 'San Guillermo, Santa Fe')

    PLANTNET_API_KEY = os.environ.get('PLANTNET_API_KEY')
    AGROMONITORING_API_KEY = os.environ.get('AGROMONITORING_API_KEY')
