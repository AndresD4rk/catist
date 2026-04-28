from . import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True ) # ID estático para el ejemplo
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    listas = db.relationship('Lista', backref='categoria', lazy=True)

class Lista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cat_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    
    items = db.relationship('Item', backref='lista', lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('lista.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200), nullable=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False)
    imagen_url = db.Column(db.String(200), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "list_id": self.list_id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "fecha_creacion": self.fecha_creacion.isoformat(),
            "imagen_url": self.imagen_url,            
            "lista": self.lista.id if self.lista else None,
            "categoria": self.lista.categoria.nombre if self.lista and self.lista.categoria else None,
        }