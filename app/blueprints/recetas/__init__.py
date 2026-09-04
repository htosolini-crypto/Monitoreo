from flask import Blueprint

bp = Blueprint('recetas', __name__, url_prefix='/recetas')

from app.blueprints.recetas import routes  # noqa: E402,F401
