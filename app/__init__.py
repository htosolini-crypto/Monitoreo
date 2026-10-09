import os
import secrets

import click
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import Config
from app.extensions import db, migrate, mail, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    if not app.config.get('SECRET_KEY'):
        raise RuntimeError(
            'Falta la variable de entorno SECRET_KEY. Definila en el archivo .env (local) '
            'o en las variables del servicio (producción).'
        )

    # Detrás del proxy de Railway: respeta X-Forwarded-Proto/Host para que url_for(_external=True)
    # genere links https con el dominio público. Sin esos headers (desarrollo local) no tiene efecto.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.models import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.clientes import bp as clientes_bp
    from app.blueprints.productos import bp as productos_bp
    from app.blueprints.principios_activos import bp as principios_activos_bp
    from app.blueprints.lotes import bp as lotes_bp
    from app.blueprints.campanias import bp as campanias_bp
    from app.blueprints.recetas import bp as recetas_bp
    from app.blueprints.usuarios import bp as usuarios_bp
    from app.blueprints.estadisticas import bp as estadisticas_bp
    from app.blueprints.parametros import bp as parametros_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(principios_activos_bp)
    app.register_blueprint(lotes_bp)
    app.register_blueprint(campanias_bp)
    app.register_blueprint(recetas_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(estadisticas_bp)
    app.register_blueprint(parametros_bp)

    from flask import render_template
    from flask_login import login_required, current_user

    from app.services.clima import obtener_clima
    from app.services.cotizaciones import obtener_cotizaciones_dolar
    from app.services.indicadores import obtener_indicadores

    @app.route('/')
    @login_required
    def dashboard():
        indicadores = None
        if current_user.is_admin or current_user.puede_recetas:
            indicadores = obtener_indicadores()

        return render_template(
            'dashboard.html',
            clima=obtener_clima(),
            cotizaciones=obtener_cotizaciones_dolar(),
            indicadores=indicadores,
        )

    @app.cli.command('seed-admin')
    def seed_admin():
        """Crea el usuario admin inicial si no existe ningún usuario.

        Usa ADMIN_USER / ADMIN_PASSWORD / ADMIN_EMAIL si están definidas; sin contraseña,
        genera una aleatoria y la muestra una sola vez."""
        if Usuario.query.first():
            click.echo('Ya existe al menos un usuario. No se creó ninguno nuevo.')
            return

        usuario = os.environ.get('ADMIN_USER', 'admin')
        password = os.environ.get('ADMIN_PASSWORD')
        generada = not password
        if generada:
            password = secrets.token_urlsafe(12)
        elif len(password) < 8:
            raise click.ClickException('ADMIN_PASSWORD debe tener al menos 8 caracteres.')

        admin = Usuario(
            usuario=usuario,
            email=os.environ.get('ADMIN_EMAIL') or None,
            is_admin=True,
            activo=True,
            puede_clientes=True,
            puede_lotes=True,
            puede_productos=True,
            puede_recetas=True,
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()

        if generada:
            click.echo(
                f'Usuario administrador creado: {usuario} / contraseña generada: {password} '
                '(anotala ahora y cambiala al ingresar; no se vuelve a mostrar).'
            )
        else:
            click.echo(f'Usuario administrador creado: {usuario}.')

    @app.cli.command('seed-parametros')
    def seed_parametros():
        """Carga los ítems iniciales de los combos (Condición IVA, Unidad, Tipo de Insumo) si la tabla está vacía."""
        from app.models import Parametro

        if Parametro.query.first():
            click.echo('Ya existen parámetros cargados. No se agregó ninguno nuevo.')
            return

        iniciales = {
            'condicion_iva': [
                ('IVA Responsable Inscripto', None),
                ('IVA Sujeto Exento', None),
                ('Consumidor Final', None),
                ('Responsable Monotributo', None),
                ('Sujeto No Categorizado', None),
                ('Proveedor del Exterior', None),
                ('Cliente del Exterior', None),
                ('IVA Liberado - Ley Nro. 19.640', None),
                ('Monotributista Social', None),
                ('IVA No Alcanzado', None),
                ('Monotributista Independiente', None),
            ],
            'unidad_producto': [
                ('Gramos', 'Grs.'),
                ('Kilogramos', 'Kgs.'),
                ('Litros', 'Lts.'),
                ('Centimetros 3', 'Cm3'),
            ],
            'tipo_insumo': [
                ('Herbicida', None),
                ('Insecticida', None),
                ('Fungicida', None),
                ('Coadyuvante', None),
                ('Fertilizante', None),
            ],
        }

        total = 0
        for categoria, items in iniciales.items():
            for orden, (valor, abreviatura) in enumerate(items):
                db.session.add(Parametro(categoria=categoria, valor=valor, abreviatura=abreviatura, orden=orden))
                total += 1

        db.session.commit()
        click.echo(f'Se cargaron {total} parámetros iniciales en {len(iniciales)} categorías.')

    return app
