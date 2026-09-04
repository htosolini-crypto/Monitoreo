from functools import wraps

from flask import redirect, url_for, flash
from flask_login import current_user, login_required


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash('No tenés permisos para acceder a esa sección.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated


def tiene_permiso_modulo(campo_permiso):
    return current_user.is_authenticated and (current_user.is_admin or getattr(current_user, campo_permiso, False))
