from datetime import datetime

from app.extensions import db


class Lote(db.Model):
    __tablename__ = 'lotes'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    cultivo = db.Column(db.String(100))
    superficie_ha = db.Column(db.Float, nullable=False, default=0.0)
    latitud = db.Column(db.String(50))
    longitud = db.Column(db.String(50))
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_alta = db.Column(db.DateTime, default=datetime.utcnow)

    recetas = db.relationship('Receta', backref='lote')
