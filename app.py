from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import sqlite3

app = Flask(__name__)
app.secret_key = "clave_secreta"

# LOGIN
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# CREAR BASE SQLITE
def get_db():
    return sqlite3.connect("usuarios.db")

# CREAR TABLA SI NO EXISTE
def crear_tabla():
    conexion = get_db()
    cursor = conexion.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        email TEXT,
        password TEXT
    )
    """)
    conexion.commit()
    conexion.close()

crear_tabla()

# MODELO USUARIO
class Usuario(UserMixin):
    def __init__(self, id, nombre, email, password):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password

# CARGAR USUARIO
@login_manager.user_loader
def load_user(user_id):
    conexion = get_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id=?", (user_id,))
    usuario = cursor.fetchone()
    conexion.close()

    if usuario:
        return Usuario(usuario[0], usuario[1], usuario[2], usuario[3])
    return None

# INICIO
@app.route("/")
def home():
    return redirect("/login")

# REGISTRO
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]

        conexion = get_db()
        cursor = conexion.cursor()

        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)",
            (nombre, email, password)
        )
        conexion.commit()
        conexion.close()

        return redirect("/login")

    return render_template("registro.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conexion = get_db()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT * FROM usuarios WHERE email=? AND password=?",
            (email, password)
        )
        usuario = cursor.fetchone()
        conexion.close()

        if usuario:
            user = Usuario(usuario[0], usuario[1], usuario[2], usuario[3])
            login_user(user)
            return redirect("/panel")

    return render_template("login.html")

# LOGOUT
@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")

# PANEL
@app.route("/panel")
@login_required
def panel():
    productos = [
        {"id": 1, "nombre": "Vestido Quito Floral", "precio": 45.99, "cantidad": 12},
        {"id": 2, "nombre": "Blusa Andina", "precio": 28.50, "cantidad": 25},
        {"id": 3, "nombre": "Jeans Quito Premium", "precio": 69.99, "cantidad": 8},
        {"id": 4, "nombre": "Zapatos Tacón", "precio": 89.99, "cantidad": 6}
    ]
    return render_template("panel.html", productos=productos)

if __name__ == "__main__":
    app.run(debug=True)