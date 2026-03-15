from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "¡Flask FUNCIONA!"

@app.route('/test')
def test():
    return "¡Flask OK! Ruta /test"

if __name__ == '__main__':
    print("🚀 Flask iniciando...")
    app.run(debug=True, host='127.0.0.1', port=5000)
