from app.extensions import db


class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    denominacion_comercial = db.Column(db.String(150), nullable=False)
    principio_activo_id = db.Column(db.Integer, db.ForeignKey('principios_activos.id'), nullable=False)
    concentracion = db.Column(db.Float, nullable=False, default=0.0)
    marca = db.Column(db.String(100), nullable=False)
    unidad = db.Column(db.String(20), nullable=False)
    precio = db.Column(db.Float, nullable=False, default=0.0)
    id_insumo = db.Column(db.String(100), nullable=True)

    principio_activo = db.relationship('PrincipioActivo', back_populates='productos')
