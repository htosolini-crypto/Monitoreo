from app.extensions import db


class Parametro(db.Model):
    __tablename__ = 'parametros'
    __table_args__ = (
        db.UniqueConstraint('categoria', 'valor', name='uq_parametro_categoria_valor'),
    )

    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(50), nullable=False)
    valor = db.Column(db.String(150), nullable=False)
    orden = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    @classmethod
    def opciones(cls, categoria):
        items = (
            cls.query.filter_by(categoria=categoria, activo=True)
            .order_by(cls.orden.asc(), cls.id.asc())
            .all()
        )
        return [(p.valor, p.valor) for p in items]
