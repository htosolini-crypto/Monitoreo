from datetime import datetime

from app.extensions import db


class Receta(db.Model):
    __tablename__ = 'recetas'

    id = db.Column(db.Integer, primary_key=True)
    numero_receta = db.Column(db.String(20), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    lote_id = db.Column(db.Integer, db.ForeignKey('lotes.id'), nullable=False)
    campania_id = db.Column(db.Integer, db.ForeignKey('campanias.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    hectareas = db.Column(db.Float, nullable=False, default=0.0)
    observaciones = db.Column(db.Text)

    campania = db.relationship('Campania')

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
