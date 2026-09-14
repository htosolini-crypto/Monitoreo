from app.extensions import db


class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    cuit = db.Column(db.String(20))
    razon_social = db.Column(db.String(150), nullable=False)
    domicilio = db.Column(db.String(150))
    numero = db.Column(db.String(20))
    codigo_postal = db.Column(db.String(20))
    localidad = db.Column(db.String(100))
    telefono = db.Column(db.String(50))
    email = db.Column(db.String(150))
    id_coniva = db.Column(db.String(100))
    enlace_maps = db.Column(db.String(500))
    latitud = db.Column(db.String(50))
    longitud = db.Column(db.String(50))

    lotes = db.relationship('Lote', backref='cliente', cascade='all, delete-orphan')
    recetas = db.relationship('Receta', backref='cliente')
