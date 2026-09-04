from flask import Blueprint

bp = Blueprint('productos', __name__, url_prefix='/productos')

from app.blueprints.productos import routes  # noqa: E402,F401
