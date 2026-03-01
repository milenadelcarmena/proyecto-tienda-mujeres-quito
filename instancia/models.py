import sqlite3
from typing import Dict, List, Optional, Set

class Producto:
    def __init__(self, id_producto: int, nombre: str, cantidad: int, precio: float, categoria: str = ""):
        self.id_producto = id_producto
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio
        self.categoria = categoria
    
    def to_dict(self) -> Dict:
        return {
            'id_producto': self.id_producto,
            'nombre': self.nombre,
            'cantidad': self.cantidad,
            'precio': self.precio,
            'categoria': self.categoria
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Producto':
        return cls(data['id_producto'], data['nombre'], data['cantidad'], data['precio'], data.get('categoria', ''))

class Inventario:
    def __init__(self, db_path: str = "instancia/inventario.db"):
        self.db_path = db_path
        self.productos_dict: Dict[int, Producto] = {}
        self.nombres_set: Set[str] = set()
        self.inicializar_db()
        self.cargar_desde_db()
    
    def conectar_db(self) -> sqlite3.Connection:
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
                precio REAL NOT NULL,
                categoria TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def cargar_desde_db(self):
        conn = self.conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos ORDER BY id_producto")
        rows = cursor.fetchall()
        self.productos_dict.clear()
        self.nombres_set.clear()
        for row in rows:
            producto = Producto.from_dict(dict(row))
            self.productos_dict[producto.id_producto] = producto
            self.nombres_set.add(producto.nombre)
        conn.close()
    
    def agregar_producto(self, nombre: str, cantidad: int, precio: float, categoria: str = "") -> bool:
        if nombre in self.nombres_set: return False
        conn = self.conectar_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO productos (nombre, cantidad, precio, categoria) VALUES (?, ?, ?, ?)",
                      (nombre, cantidad, precio, categoria))
        conn.commit()
        conn.close()
        self.cargar_desde_db()
        return True
    
    def eliminar_producto(self, id_producto: int) -> bool:
        if id_producto not in self.productos_dict: return False
        conn = self.conectar_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id_producto = ?", (id_producto,))
        conn.commit()
        conn.close()
        self.cargar_desde_db()
        return True
    
    def buscar_por_nombre(self, nombre_parcial: str) -> List[Producto]:
        return [p for p in self.productos_dict.values() if nombre_parcial.lower() in p.nombre.lower()]
    
    def obtener_todos(self) -> List[Producto]:
        return sorted(self.productos_dict.values(), key=lambda p: p.id_producto)
    
    def valor_total(self) -> float:
        return sum(p.cantidad * p.precio for p in self.productos_dict.values())
