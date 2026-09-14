from datetime import datetime

from app.extensions import db


class Lote(db.Model):
    __tablename__ = 'lotes'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    superficie_ha = db.Column(db.Float, nullable=False, default=0.0)
    enlace_maps = db.Column(db.String(500))
    latitud = db.Column(db.String(50))
    longitud = db.Column(db.String(50))
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_alta = db.Column(db.DateTime, default=datetime.utcnow)
    poligono = db.Column(db.Text, nullable=True)
    agromonitoring_id = db.Column(db.String(50), nullable=True)

    recetas = db.relationship('Receta', backref='lote')
    campanias = db.relationship(
        'Campania', back_populates='lote', cascade='all, delete-orphan', order_by='Campania.id.desc()'
    )
