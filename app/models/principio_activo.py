from app.extensions import db


class PrincipioActivo(db.Model):
    __tablename__ = 'principios_activos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False, unique=True)

    productos = db.relationship('Producto', back_populates='principio_activo')

    def __repr__(self):
        return self.nombre

    def __str__(self):
        return self.nombre
