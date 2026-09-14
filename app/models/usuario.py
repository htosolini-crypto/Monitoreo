from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db

RESET_TOKEN_SALT = 'recuperacion-password'
RESET_TOKEN_MAX_AGE = 1800  # 30 minutos


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)
    nombre_completo = db.Column(db.String(150))
    matricula = db.Column(db.String(50))
    cuit = db.Column(db.String(20))
    domicilio = db.Column(db.String(150))
    telefono = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    puede_clientes = db.Column(db.Boolean, nullable=False, default=False)
    puede_lotes = db.Column(db.Boolean, nullable=False, default=False)
    puede_productos = db.Column(db.Boolean, nullable=False, default=False)
    puede_recetas = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def nombre_para_mostrar(self):
        return self.nombre_completo or self.usuario

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generar_token_reset(self):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(self.id, salt=RESET_TOKEN_SALT)

    @staticmethod
    def verificar_token_reset(token):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = serializer.loads(token, salt=RESET_TOKEN_SALT, max_age=RESET_TOKEN_MAX_AGE)
        except (BadSignature, SignatureExpired):
            return None
        return db.session.get(Usuario, user_id)
