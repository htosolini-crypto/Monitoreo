from flask import Blueprint

bp = Blueprint('estadisticas', __name__, url_prefix='/estadisticas')

from app.blueprints.estadisticas import routes  # noqa: E402,F401
