import sqlite3

def crear_tablas():
    conn = sqlite3.connect("stock.db")
    cursor = conn.cursor()

    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            clave TEXT
        )
    ''')

    # Insertar usuario por defecto si no existe
    cursor.execute('''
        INSERT OR IGNORE INTO usuarios (usuario, clave) VALUES (?, ?)
    ''', ('enzo', 'admin2025'))

    # Crear tabla de productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            stock_sistema INTEGER,
            stock_real INTEGER,
            precio_costo REAL,
            precio_venta REAL,
            fecha_modificacion TEXT
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    crear_tablas()
    print("Tablas creadas correctamente.")
