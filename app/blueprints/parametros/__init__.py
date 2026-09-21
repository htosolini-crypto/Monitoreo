from flask import Blueprint

bp = Blueprint('parametros', __name__, url_prefix='/parametros')

from app.blueprints.parametros import routes  # noqa: E402,F401
