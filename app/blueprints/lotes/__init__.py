from flask import Blueprint

bp = Blueprint('lotes', __name__, url_prefix='/lotes')

from app.blueprints.lotes import routes  # noqa: E402,F401
