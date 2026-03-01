from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from models import Inventario

app = Flask(__name__)
app.secret_key = 'tienda_mujeres_quito_2026'

# Instancia global del inventario
inventario = Inventario()

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

# 🚀 SUBMENÚ REQUISITOS ING - COMPLETO
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
        
        # Actualizar SQLite
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
    if id_producto == 0:  # Submenú
        if request.method == 'POST':
            id_producto = int(request.form['id_producto'])
            if inventario.eliminar_producto(id_producto):
                flash('✅ Producto eliminado correctamente!')
            else:
                flash('❌ Producto no encontrado')
            return redirect(url_for('index'))
        return render_template('eliminar.html')
    else:  # Eliminar directo tabla
        if inventario.eliminar_producto(id_producto):
            flash('✅ Producto eliminado correctamente!')
        return redirect(url_for('index'))

@app.route('/acerca')
def acerca():
    return render_template('acerca.html')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
