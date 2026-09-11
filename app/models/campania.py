from app.extensions import db


class Campania(db.Model):
    __tablename__ = 'campanias'

    id = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.Integer, db.ForeignKey('lotes.id'), nullable=False)
    nombre = db.Column(db.String(20), nullable=False)
    cultivo = db.Column(db.String(100), nullable=False)
    variedad = db.Column(db.String(100))
    fecha_siembra = db.Column(db.Date)
    fecha_cosecha = db.Column(db.Date)
    observaciones = db.Column(db.Text)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    lote = db.relationship('Lote', back_populates='campanias')

    def __repr__(self):
        return f'{self.nombre} - {self.cultivo}'

    def __str__(self):
        return f'{self.nombre} - {self.cultivo}'
