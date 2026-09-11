from flask import Blueprint

bp = Blueprint('campanias', __name__, url_prefix='/campanias')

from app.blueprints.campanias import routes  # noqa: E402,F401
