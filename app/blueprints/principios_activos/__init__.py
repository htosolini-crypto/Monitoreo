from flask import Blueprint

bp = Blueprint('principios_activos', __name__, url_prefix='/principios-activos')

from app.blueprints.principios_activos import routes  # noqa: E402,F401
