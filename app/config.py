import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-cambiar-en-produccion')

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'cultivos.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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
