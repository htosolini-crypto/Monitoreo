import os

import click
from flask import Flask

from app.config import Config
from app.extensions import db, migrate, mail, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

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
        """Crea el usuario admin inicial si no existe ningún usuario."""
        if Usuario.query.first():
            click.echo('Ya existe al menos un usuario. No se creó ninguno nuevo.')
            return

        admin = Usuario(
            usuario='admin',
            is_admin=True,
            activo=True,
            puede_clientes=True,
            puede_lotes=True,
            puede_productos=True,
            puede_recetas=True,
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        click.echo('Usuario admin creado (usuario: admin / password: admin123). Cambiá la contraseña luego de ingresar.')

    @app.cli.command('seed-parametros')
    def seed_parametros():
        """Carga los ítems de los combos fijos (Condición IVA, Unidad) si la tabla está vacía."""
        from app.models import Parametro

        if Parametro.query.first():
            click.echo('Ya existen parámetros cargados. No se agregó ninguno nuevo.')
            return

        condiciones_iva = [
            'IVA Responsable Inscripto',
            'IVA Sujeto Exento',
            'Consumidor Final',
            'Responsable Monotributo',
            'Sujeto No Categorizado',
            'Proveedor del Exterior',
            'Cliente del Exterior',
            'IVA Liberado - Ley Nro. 19.640',
            'Monotributista Social',
            'IVA No Alcanzado',
            'Monotributista Independiente',
        ]
        unidades = ['Gramos', 'Kilos', 'Litros']

        for orden, valor in enumerate(condiciones_iva):
            db.session.add(Parametro(categoria='condicion_iva', valor=valor, orden=orden))
        for orden, valor in enumerate(unidades):
            db.session.add(Parametro(categoria='unidad_producto', valor=valor, orden=orden))

        db.session.commit()
        click.echo(f'Se cargaron {len(condiciones_iva)} condiciones de IVA y {len(unidades)} unidades.')

    return app
