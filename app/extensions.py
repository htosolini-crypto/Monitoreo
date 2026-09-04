import sqlite3

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, inicia sesión para continuar.'
login_manager.login_message_category = 'warning'


@event.listens_for(Engine, 'connect')
def _habilitar_foreign_keys_sqlite(dbapi_connection, connection_record):
    """SQLite no valida FKs por defecto; sin esto, borrar un registro
    referenciado (p. ej. un cliente con recetas) corrompe datos en silencio."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()
