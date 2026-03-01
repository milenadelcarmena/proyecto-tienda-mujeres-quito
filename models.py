import sqlite3
from typing import Dict, List

class Producto:
    def __init__(self, id_producto: int, nombre: str, cantidad: int, precio: float):
        self.id_producto = id_producto
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio
    
    def to_dict(self) -> Dict:
        return {
            'id_producto': self.id_producto,
            'nombre': self.nombre,
            'cantidad': self.cantidad,
            'precio': self.precio
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Producto':
        return cls(data['id_producto'], data['nombre'], data['cantidad'], data['precio'])

class Inventario:
    def __init__(self, db_path: str = "instancia/inventario.db"):
        self.db_path = db_path
        self.productos_dict: Dict[int, Producto] = {}
        self.inicializar_db()
        self.cargar_desde_db()
    
    def conectar_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def inicializar_db(self):
        conn = self.conectar_db()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                cantidad INTEGER NOT NULL,
                precio REAL NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    
    def cargar_desde_db(self):
        conn = self.conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos")
        rows = cursor.fetchall()
        self.productos_dict.clear()
        for row in rows:
            producto = Producto.from_dict(dict(row))
            self.productos_dict[producto.id_producto] = producto
        conn.close()
    
    def agregar_producto(self, nombre: str, cantidad: int, precio: float, categoria: str = "") -> bool:
        conn = self.conectar_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
                          (nombre, cantidad, precio))
            conn.commit()
            self.cargar_desde_db()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
    
    def eliminar_producto(self, id_producto: int) -> bool:
        if id_producto not in self.productos_dict:
            return False
        conn = self.conectar_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id_producto = ?", (id_producto,))
        conn.commit()
        self.cargar_desde_db()
        conn.close()
        return True
    
    def obtener_todos(self) -> List[Producto]:
        return list(self.productos_dict.values())
    
    def valor_total(self) -> float:
        return sum(p.cantidad * p.precio for p in self.productos_dict.values())
