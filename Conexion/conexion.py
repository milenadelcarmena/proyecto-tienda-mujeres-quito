import mysql.connector

def conectar_mysql():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='tienda_mujeres_quito'
        )
        return conexion
    except:
        return None


