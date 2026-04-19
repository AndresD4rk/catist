from . import db

# Tabla de asociación entre Usuarios y Categorías
usuario_categorias = db.Table('usuario_categorias',
    db.Column('usuario_id', db.String(50), db.ForeignKey('categoria.usuario_creador')), # Simplificado para el ejemplo
    db.Column('categoria_id', db.Integer, db.ForeignKey('categoria.id')),
    db.Column('user_string_id', db.String(50)) # El ID estático que usas
)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False) # Única para que se "recicle"
    # El usuario_creador es informativo, pero la categoría puede ser usada por otros
    usuario_creador = db.Column(db.String(50))

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    usuario_id = db.Column(db.String(50), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'))
    
    # Relación para acceder fácilmente al nombre de la categoría
    categoria = db.relationship('Categoria', backref='items')