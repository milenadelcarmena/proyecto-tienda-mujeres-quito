from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import json
import csv
import sqlite3
from models import Inventario

app = Flask(__name__)
app.secret_key = 'tienda_mujeres_quito_2026'

# === CONFIGURACIÓN SQLAlchemy ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "instancia/inventario.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# === MODELO SQLAlchemy ===
class Producto(db.Model):
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)

# Instancia global del inventario
inventario = Inventario()

# === ARCHIVOS PERSISTENCIA (SEMANA 13) ===
DATA_DIR = os.path.join(BASE_DIR, 'data')  # ← CAMBIADO: sin inventario/
TXT_FILE = os.path.join(DATA_DIR, 'datos.txt')
JSON_FILE = os.path.join(DATA_DIR, 'datos.json')
CSV_FILE = os.path.join(DATA_DIR, 'datos.csv')

@app.route('/')
def index():
    productos = inventario.obtener_todos()
    valor_total = inventario.valor_total()
    total_productos = len(productos)
    return render_template('index.html', 
                         productos=productos, 
                         valor_total=valor_total,
                         total_productos=total_productos)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        
        if inventario.agregar_producto(nombre, cantidad, precio):
            flash('✅ Producto agregado correctamente!')
            return redirect(url_for('index'))
        else:
            flash('❌ Error: Producto ya existe')
    
    return render_template('agregar.html')

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    if request.method == 'POST':
        termino = request.form['busqueda'].lower()
        todos = inventario.obtener_todos()
        productos = [p for p in todos if termino in p.nombre.lower()]
        valor_total = sum(p.cantidad * p.precio for p in productos)
        total_productos = len(productos)
        return render_template('index.html', productos=productos, 
                             valor_total=valor_total, total_productos=total_productos)
    return render_template('buscar.html')

@app.route('/mostrar')
def mostrar():
    productos = inventario.obtener_todos()
    valor_total = inventario.valor_total()
    total_productos = len(productos)
    return render_template('index.html', productos=productos, 
                         valor_total=valor_total, total_productos=total_productos)

@app.route('/editar/<int:id_producto>', methods=['GET', 'POST'])
@app.route('/editar', methods=['GET', 'POST'])
def editar(id_producto=None):
    productos = inventario.obtener_todos()
    
    if request.method == 'POST':
        id_producto = int(request.form['id_producto'])
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        
        conn = sqlite3.connect('instancia/inventario.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET nombre=?, cantidad=?, precio=? WHERE id_producto=?", 
                      (nombre, cantidad, precio, id_producto))
        if cursor.rowcount > 0:
            conn.commit()
            flash('✅ Producto actualizado correctamente!')
        else:
            flash('❌ Producto no encontrado')
        conn.close()
        inventario.cargar_desde_db()
        return redirect(url_for('index'))
    
    return render_template('editar.html', productos=productos, id_producto=id_producto)

@app.route('/eliminar/<int:id_producto>', methods=['GET', 'POST'])
def eliminar(id_producto):
    if id_producto == 0:
        if request.method == 'POST':
            id_producto = int(request.form['id_producto'])
            if inventario.eliminar_producto(id_producto):
                flash('✅ Producto eliminado correctamente!')
            else:
                flash('❌ Producto no encontrado')
            return redirect(url_for('index'))
        return render_template('eliminar.html')
    else:
        if inventario.eliminar_producto(id_producto):
            flash('✅ Producto eliminado correctamente!')
        return redirect(url_for('index'))

@app.route('/acerca')
def acerca():
    return render_template('acerca.html')

# === SEMANA 13 - PERSISTENCIA ===
@app.route('/datos')
def ver_datos():
    # Crear directorio si no existe
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Leer TXT
    lineas_txt = []
    if os.path.exists(TXT_FILE):
        with open(TXT_FILE, 'r', encoding='utf-8') as f:
            lineas_txt = f.readlines()
    
    # Leer JSON
    datos_json = []
    if os.path.exists(JSON_FILE) and os.path.getsize(JSON_FILE) > 0:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            datos_json = json.load(f)
    
    # Leer CSV
    datos_csv = []
    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            datos_csv = list(reader)
    
    # Leer SQLite
    productos = Producto.query.all()
    
    return render_template('datos.html', 
                         lineas_txt=lineas_txt,
                         datos_json=datos_json,
                         datos_csv=datos_csv,
                         productos=productos)

@app.route('/producto/nuevo', methods=['GET', 'POST'])
def producto_nuevo():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = float(request.form['precio'])
        cantidad = int(request.form['cantidad'])
        
        # Crear directorio automáticamente
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # 1. SQLite
        prod = Producto(nombre=nombre, precio=precio, cantidad=cantidad)
        db.session.add(prod)
        db.session.commit()
        
        # 2. Registro
        registro = {
            "id": prod.id_producto,
            "nombre": nombre,
            "precio": precio,
            "cantidad": cantidad
        }
        
        # 3. TXT
        with open(TXT_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{registro}\n")
        
        # 4. JSON
        datos_json = []
        if os.path.exists(JSON_FILE) and os.path.getsize(JSON_FILE) > 0:
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                datos_json = json.load(f)
        datos_json.append(registro)
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(datos_json, f, ensure_ascii=False, indent=2)
        
        # 5. CSV
        file_exists = os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'nombre', 'precio', 'cantidad'])
            if not file_exists:
                writer.writeheader()
            writer.writerow(registro)
        
        flash('✅ ¡Guardado en 4 formatos!')
        return redirect(url_for('ver_datos'))
    
    return render_template('producto_form.html')

# Crear tablas
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
