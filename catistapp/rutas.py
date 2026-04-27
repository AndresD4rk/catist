from flask import Blueprint, json, redirect, render_template, request, jsonify, url_for
from wtforms import StringField
from flask_login import current_user, login_required, login_user
from catistapp.controller import LoginForm, RegistroForm, AddCategoria
from .modelos import Item, Categoria, Lista, User
from . import db

main = Blueprint('main', __name__)
USUARIO_ACTUAL = "usuario_demo_1"

@main.route('/')
def index():
    return render_template('index.html', titulo="Inicio")

@main.route('/catist')
@login_required
def catist_page():
    cat = Categoria.query.all()
    categorias_nombres = [c.nombre for c in cat]
    mis_listas = Lista.query.filter_by(user_id=current_user.id).all()
    if not mis_listas: 
        print(f"No se encontraron listas para el usuario actual. Categorías disponibles: {categorias_nombres}")
        return render_template('catist.html', listas_json=json.dumps(categorias_nombres))
    mis_items = Item.query.filter_by(list_id=mis_listas[0].id).all()

    # print("--- DEBUG CATIST ---")
    # print(f"Listas encontradas: {mis_listas}")
    # print(f"Items encontrados: {mis_items}")
    # print(f"Categorías disponibles: {categorias_nombres}")
    return render_template('catist.html', listas=mis_listas, items=mis_items,categorias=categorias_nombres) 

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

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form = LoginForm()
        print("--- DATOS RECIBIDOS ---")
        print(form.data)
        if form.validate_on_submit():
            # Aquí iría la lógica para crear el usuario en la base de datos
            email=User.query.filter_by(email=form.email.data).first()

            if email and email.password == form.password.data:
                #return render_template('catist.html', form=LoginForm())
                login_user(email)
                return redirect(url_for('main.catist_page'))
    return render_template('login.html', form=LoginForm(), titulo="Login")

@main.route('/register', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        form = RegistroForm()
        if form.validate_on_submit():
            print("Entrando a registro1")
            # Aquí iría la lógica para crear el usuario en la base de datos
            email = form.email.data
            password = form.password.data
            confirmar = form.confirmar.data
        
            if password != confirmar:
                return "Las contraseñas no coinciden"
            else:
                nuevo_usuario = User(email=email, password=password)
                db.session.add(nuevo_usuario)
                db.session.commit()
                login_user(nuevo_usuario)
                return redirect(url_for('main.catist_page'))
                #return render_template('catist.html', form=LoginForm())
       
    return render_template('register.html', form=RegistroForm(), titulo="Registro")

@main.route('/api/addcategoria', methods=['POST'])
def add_categoria():
    nombre_cat = request.json.get('nombre', '').strip()
    categoria = Categoria.query.filter_by(nombre=nombre_cat).first()
    print(f"Buscando categoría: '{nombre_cat}' - Encontrada: {categoria is not None}")
    
    if not categoria:
        # Si no existe, se crea de cero
        categoria = Categoria(nombre=nombre_cat)
        db.session.add(categoria)
        db.session.commit()
    
    return jsonify({"success": True, "id": categoria.id, "nombre": categoria.nombre})


@main.route('/api/additem', methods=['POST'])
def add_item():
    nombre_item = request.json.get('nombre', '').strip()
    categoria_item = request.json.get('categoria', '').strip()
    descripcion_item = request.json.get('descripcion', '').strip()
    imagen_item = request.json.get('imagen', '').strip()
    print(f"Recibido nuevo item: Nombre='{nombre_item}', Categoría='{categoria_item}', Descripción='{descripcion_item}', Imagen='{imagen_item}'")
    if not nombre_item or not categoria_item:
        return jsonify({"success": False, "message": "Nombre y categoría son requeridos"}), 400
    lista=Lista.query.filter_by(user_id=current_user.id, cat_id=categoria_item).first()  
    if not lista:
        db.session.add(Lista(user_id=current_user.id, cat_id=categoria_item))
        db.session.commit()
        lista=Lista.query.filter_by(user_id=current_user.id, cat_id=categoria_item).first()
        if not lista:
            print(f"No se pudo crear la lista para categoría {categoria_item}")
        else:
            db.session.add(Item(nombre=nombre_item, descripcion=descripcion_item, imagen_url=imagen_item, list_id=lista.id, fecha_creacion=db.func.now()))            
            db.session.commit()       
        return jsonify({"success": True, "message": "Lista creada y item agregado"})
    else:        
        db.session.add(Item(nombre=nombre_item, descripcion=descripcion_item, imagen_url=imagen_item, list_id=lista.id, fecha_creacion=db.func.now()))
        db.session.commit()
        print(f"Lista encontrada: {lista.id} para categoría {categoria_item}")
        return jsonify({"success": True, "message": "Item agregado a lista existente"})
    

@main.route('/api/getitems', methods=['GET'])
def get_items():
    mis_items = Item.query.filter_by(user_id=current_user.id).all()
    return jsonify({"success": True, "items": [item.to_dict() for item in mis_items]})