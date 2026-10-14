from app.extensions import db
from app.models.parametro import Parametro


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

    @property
    def unidad_abreviada(self):
        """Abreviatura de la unidad según Parámetros (unidad_producto); si no tiene, la unidad tal cual."""
        parametro = Parametro.query.filter_by(categoria='unidad_producto', valor=self.unidad).first()
        return (parametro.abreviatura if parametro and parametro.abreviatura else self.unidad)
