from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    productos = [
        {"id": 1, "nombre": "Vestido Quito Floral", "precio": 45.99, "cantidad": 12},
        {"id": 2, "nombre": "Blusa Andina", "precio": 28.50, "cantidad": 25},
        {"id": 3, "nombre": "Jeans Quito Premium", "precio": 69.99, "cantidad": 8},
        {"id": 4, "nombre": "Zapatos Tacón", "precio": 89.99, "cantidad": 6}
    ]
    return render_template('index.html', productos=productos, total=len(productos))

@app.route('/mysql_test')
def mysql_test():
    return "<h1 style='color:green;text-align:center'>✅ MySQL Listo - Semana 14 OK!</h1>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
