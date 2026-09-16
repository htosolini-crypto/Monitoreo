from datetime import datetime

from itsdangerous import URLSafeTimedSerializer, BadSignature
from flask import current_app

from app.extensions import db

TOKEN_PUBLICO_SALT = 'receta-publica'


class Receta(db.Model):
    __tablename__ = 'recetas'

    id = db.Column(db.Integer, primary_key=True)
    numero_receta = db.Column(db.String(20), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    lote_id = db.Column(db.Integer, db.ForeignKey('lotes.id'), nullable=False)
    campania_id = db.Column(db.Integer, db.ForeignKey('campanias.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    hectareas = db.Column(db.Float, nullable=False, default=0.0)
    observaciones = db.Column(db.Text)

    campania = db.relationship('Campania')
    profesional = db.relationship('Usuario')

    detalles = db.relationship(
        'RecetaDetalle', backref='receta', cascade='all, delete-orphan'
    )

    @staticmethod
    def generar_numero(session):
        anio_actual = datetime.now().strftime('%Y')
        prefijo = f"{anio_actual}-"

        ultima = (
            session.query(Receta)
            .filter(Receta.numero_receta.like(f"{prefijo}%"))
            .order_by(Receta.id.desc())
            .first()
        )

        if ultima:
            ultimo_num = int(ultima.numero_receta.split('-')[1])
            nuevo_num = ultimo_num + 1
        else:
            nuevo_num = 1

        return f"{prefijo}{nuevo_num:04d}"

    def generar_token_publico(self):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(self.id, salt=TOKEN_PUBLICO_SALT)

    @staticmethod
    def verificar_token_publico(token):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            receta_id = serializer.loads(token, salt=TOKEN_PUBLICO_SALT)
        except BadSignature:
            return None
        return db.session.get(Receta, receta_id)


class RecetaDetalle(db.Model):
    __tablename__ = 'recetas_detalle'

    id = db.Column(db.Integer, primary_key=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    dosis = db.Column(db.Float, nullable=False, default=0.0)
    cantidad_total = db.Column(db.Float, nullable=False, default=0.0)
    precio_unitario = db.Column(db.Float, nullable=False, default=0.0)
    importe_total = db.Column(db.Float, nullable=False, default=0.0)

    producto = db.relationship('Producto')
