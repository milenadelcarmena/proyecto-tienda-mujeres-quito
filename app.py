from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>🏪 Bienvenido a Tienda Mujeres Quito</h1>
    <p>Catálogo de ropa y accesorios para mujeres. Ofertas especiales en Quito y Cayambe.</p>
    <ul>
        <li>Blusas desde $15</li>
        <li>Vestidos en tendencia</li>
        <li>Accesorios modernos</li>
    </ul>
    <a href="/producto/blusa">Ver Blusa ejemplo</a>
    '''

@app.route('/producto/<nombre>')
def producto(nombre):
    return f'''
    <h2>Producto: {nombre.title()}</h2>
    <p>✅ Disponible en Tienda Mujeres Quito. Precio: $20. Envío a Quito gratis.</p>
    <a href="/">← Volver al catálogo</a>
    '''

if __name__ == '__main__':
    app.run(debug=True)
