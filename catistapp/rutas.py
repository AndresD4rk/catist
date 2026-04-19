from flask import Blueprint, render_template, request, jsonify
from .modelos import Item, Categoria
from . import db

main = Blueprint('main', __name__)
USUARIO_ACTUAL = "usuario_demo_1"

@main.route('/')
def index():
    return render_template('index.html', titulo="Inicio")

@main.route('/catist')
def catist_page():
    # Obtener categorías que el usuario ha "agregado" o usa
    # Por simplicidad en este ejemplo, mostramos todas las categorías que existen en la DB
    todas_las_categorias = Categoria.query.all()
    items_db = Item.query.filter_by(usuario_id=USUARIO_ACTUAL).all()
    
    return render_template('catist.html', 
                           items=items_db, 
                           categorias=todas_las_categorias) 

@main.route('/api/categorias', methods=['POST'])
def agregar_categoria():
    data = request.get_json()
    nombre_cat = data['nombre'].strip()
    
    # Lógica de reciclaje: ¿Ya existe esta categoría en el sistema?
    categoria = Categoria.query.filter_by(nombre=nombre_cat).first()
    
    if not categoria:
        # Si no existe, se crea de cero
        categoria = Categoria(nombre=nombre_cat, usuario_creador=USUARIO_ACTUAL)
        db.session.add(categoria)
        db.session.commit()
    
    return jsonify({"success": True, "id": categoria.id, "nombre": categoria.nombre})

@main.route('/api/items', methods=['POST'])
def agregar_item():
    data = request.get_json()
    # Buscamos la categoría por nombre (la que seleccionó el usuario)
    categoria = Categoria.query.filter_by(nombre=data['categoria']).first()
    
    nuevo_item = Item(
        nombre=data['nombre'],
        categoria_id=categoria.id,
        usuario_id=USUARIO_ACTUAL
    )
    db.session.add(nuevo_item)
    db.session.commit()
    return jsonify({"success": True, "id": nuevo_item.id})

@main.route('/api/items/<int:id>', methods=['DELETE'])
def eliminar_item(id):
    item = Item.query.get_or_404(id)
    if item.usuario_id == USUARIO_ACTUAL:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False}), 403