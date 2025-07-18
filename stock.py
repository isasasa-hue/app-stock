# app_stock.py
from flask import Flask, request, redirect, url_for, session
import sqlite3
from crear_tablas import crear_tablas
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'stock2025'
DB = 'stock.db'
crear_tablas()

# --- ESTILO EN ROJO ---
base_style = """
<style>
    body {
        background-color: #ffe6e6;
        font-family: Arial, sans-serif;
        text-align: center;
        margin: 0;
        padding: 20px;
    }
   h2 {
    color: #800000;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 3em;
    font-weight: 700;
    text-align: center;
    margin-bottom: 30px;
    background: linear-gradient(90deg, #b30000, #660000);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

    form, table {
        background-color: white;
        display: inline-block;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 0px 10px #aaa;
        margin-top: 20px;
        text-align: left;
    }
    th, td {
        padding: 10px;
        border: 1px solid #ccc;
        text-align: center;
    }
    a {
        display: block;
        margin-top: 20px;
        color: #800000;
        text-decoration: none;
        font-weight: bold;
    }
    a:hover {
        color: #4d0000;
    }
    input[type=text], input[type=password], input[type=date], input[type=number] {
        width: 100%;
        padding: 8px;
        margin: 6px 0 12px 0;
        box-sizing: border-box;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 16px;
    }
    input[type=submit], button {
        background-color: #800000;
        color: white;
        border: none;
        padding: 10px 25px;
        cursor: pointer;
        font-weight: bold;
        border-radius: 5px;
        font-size: 16px;
    }
    input[type=submit]:hover, button:hover {
        background-color: #4d0000;
    }
    .watermark {
        position: fixed;
        top: 10px;
        left: 10px;
        opacity: 0.5;
        font-size: 14px;
        color: #800000;
        font-weight: bold;
        font-family: Arial, sans-serif;
        user-select: none;
        pointer-events: none;
        z-index: 9999;
    }
    .error {
        color: red;
        font-weight: bold;
        margin-top: 10px;
    }
    .hint {
        color: #800000;
        font-style: italic;
        font-size: 14px;
        margin-top: 5px;
    }
</style>
"""

def page_template(title, body_html):
    return f'''
    <html>
    <head>
        <title>{title}</title>
        {base_style}
    </head>
    <body>
        <h2>{title}</h2>
        {body_html}
        <div class="watermark">Designed by: Jvandekoppel</div>
    </body>
    </html>
    '''

# --- LOGIN ---
@app.route('/', methods=['GET', 'POST'])
def login():
    mensaje = ''
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        clave = request.form.get('clave')
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT clave FROM usuarios WHERE usuario = ?", (usuario,))
        fila = c.fetchone()
        conn.close()
        if fila and fila[0] == clave:
            session['logueado'] = True
            session['usuario'] = usuario
            return redirect(url_for('menu'))
        else:
            mensaje = '<p class="error">Usuario o contraseña incorrectos</p><a href="/recuperar">¿Olvidaste tu contraseña?</a>'
    return page_template("Iniciar sesión", f'''
        <form method="POST">
            Usuario: <input type="text" name="usuario" required><br>
            Clave: <input type="password" name="clave" required><br>
            <input type="submit" value="Entrar">
        </form>
        {mensaje}
    ''')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- CAMBIAR CONTRASEÑA DESDE MENÚ ---
@app.route('/cambiar_clave', methods=['GET', 'POST'])
def cambiar_clave():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    mensaje = ''
    if request.method == 'POST':
        actual = request.form.get('actual')
        nueva = request.form.get('nueva')
        usuario = session.get('usuario')
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT clave FROM usuarios WHERE usuario = ?", (usuario,))
        fila = c.fetchone()
        if fila and fila[0] == actual:
            c.execute("UPDATE usuarios SET clave = ? WHERE usuario = ?", (nueva, usuario))
            conn.commit()
            mensaje = '<p style="color:green;">✅ Contraseña actualizada.</p>'
        else:
            mensaje = '<p class="error">❌ Contraseña actual incorrecta.</p>'
        conn.close()
    form = '''
    <form method="POST">
        Clave actual: <input type="password" name="actual" required><br>
        Nueva clave: <input type="password" name="nueva" required><br>
        <input type="submit" value="Cambiar clave">
    </form>
    <a href="/menu">Volver al menú</a>
    '''
    return page_template("Cambiar Contraseña", form + mensaje)

# --- PÁGINA PARA RECUPERAR CONTRASEÑA (USUARIO, CLAVE ACTUAL, NUEVA CON CONFIRMACIÓN) ---
@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    mensaje = ''
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        nueva1 = request.form.get('nueva1')
        nueva2 = request.form.get('nueva2')
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT clave FROM usuarios WHERE usuario = ?", (usuario,))
        fila = c.fetchone()
        if fila:
            if nueva1 == nueva2:
                c.execute("UPDATE usuarios SET clave = ? WHERE usuario = ?", (nueva1, usuario))
                conn.commit()
                mensaje = '<p style="color:green;">✅ Contraseña cambiada con éxito. Ya podés iniciar sesión.</p>'
            else:
                mensaje = '<p class="error">❌ Las nuevas contraseñas no coinciden.</p>'
        else:
            mensaje = '<p class="error">❌ Usuario no encontrado.</p>'
        conn.close()

    form = f'''
    <form method="POST">
        Usuario: <input type="text" name="usuario" required><br>
        Nueva contraseña: <input type="password" name="nueva1" required><br>
        Repetir nueva contraseña: <input type="password" name="nueva2" required><br>
        <input type="submit" value="Cambiar contraseña">
    </form>
    <a href="/">Volver a iniciar sesión</a>
    {mensaje}
    '''
    return page_template("Recuperar Contraseña", form)


# --- MENÚ ---
@app.route('/menu')
def menu():
    if not session.get('logueado'):
        return redirect(url_for('login'))

    opciones = '''
    <style>
        .menu-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
            margin-top: 40px;
        }
        .menu-button {
            background-color: #800000;
            color: white;
            font-weight: bold;
            font-size: 20px;
            padding: 15px 40px;
            border-radius: 12px;
            text-decoration: none;
            box-shadow: 0 4px 10px rgba(128, 0, 0, 0.5);
            width: 280px;
            text-align: center;
            transition: background-color 0.3s ease, transform 0.2s ease;
            user-select: none;
        }
        .menu-button:hover {
            background-color: #b30000;
            transform: scale(1.05);
            box-shadow: 0 6px 14px rgba(179, 0, 0, 0.7);
        }
    </style>

    <div class="menu-container">
        <a href="/agregar" class="menu-button">1. Agregar producto</a>
        <a href="/editar" class="menu-button">2. Editar producto</a>
        <a href="/comparar" class="menu-button">3. Historial de stock</a>
        <a href="/eliminar" class="menu-button">4. Eliminar producto</a>
        <a href="/cambiar_clave" class="menu-button">5. Cambiar clave</a>
        <a href="/logout" class="menu-button">Salir</a>
    </div>
    '''
    return page_template("Menú Principal", opciones)

# RUTA AGREGAR PRODUCTO
@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    mensaje = ''

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        stock_sistema = request.form.get('stock_sistema')
        stock_real = request.form.get('stock_real')
        precio_costo = request.form.get('precio_costo')
        precio_venta = request.form.get('precio_venta')
        # Fecha y hora actuales en servidor (string)
        fecha_mod = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        # Verificamos si el producto ya existe
        c.execute("SELECT * FROM productos WHERE nombre = ?", (nombre,))
        producto_existente = c.fetchone()

        if producto_existente:
            # Actualizamos producto
            c.execute('''
                UPDATE productos
                SET stock_sistema = ?, stock_real = ?, precio_costo = ?, precio_venta = ?, fecha_modificacion = ?
                WHERE nombre = ?
            ''', (stock_sistema, stock_real, precio_costo, precio_venta, fecha_mod, nombre))
            mensaje = '<p style="color:orange;">Producto actualizado.</p>'
        else:
            # Insertamos nuevo producto
            c.execute('''
                INSERT INTO productos (nombre, stock_sistema, stock_real, precio_costo, precio_venta, fecha_modificacion)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nombre, stock_sistema, stock_real, precio_costo, precio_venta, fecha_mod))
            mensaje = '<p style="color:green;">Producto agregado.</p>'

        conn.commit()
        conn.close()

    form = '''
    <form method="POST">
        <p><strong>Fecha y hora actual:</strong></p>
        <p>Fecha última modificación: 
          <input type="datetime-local" name="fecha_modificacion" id="fecha_modificacion" readonly>
        </p>

        Nombre: <input type="text" name="nombre" required><br>
        Stock en sistema: <input type="number" name="stock_sistema" required><br>
        Stock real: <input type="number" name="stock_real" required><br>
        Precio de costo: <input type="number" step="0.01" name="precio_costo" required><br>
        Precio de venta: <input type="number" step="0.01" name="precio_venta" required><br>
        <input type="submit" value="Agregar producto">
    </form>
    <a href="/menu">Volver al menú</a>

    <script>
        function formatDateLocal(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            return `${year}-${month}-${day}T${hours}:${minutes}`;
        }

        function actualizarFechaHora() {
            const ahora = new Date();
            const formato = formatDateLocal(ahora);
            document.getElementById("fecha_modificacion").value = formato;
        }

        actualizarFechaHora();
        setInterval(actualizarFechaHora, 1000);
    </script>
    '''
    return page_template("Agregar Producto", form + mensaje)


# RUTA COMPARAR STOCK (Muestra diferencias)
@app.route('/comparar')
def comparar():
    if not session.get('logueado'):
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT nombre, stock_sistema, stock_real, precio_costo, precio_venta, fecha_modificacion FROM productos')
    productos = c.fetchall()
    conn.close()

    filas = ''
    for p in productos:
        nombre, s_sis, s_real, p_costo, p_venta, fecha = p
        dif = s_real - s_sis
        if dif == 0:
            estado = 'No hay diferencia s'
        elif dif < 0:
            unidades = abs(dif)
            monto = unidades * p_venta
            estado = f'Faltan {unidades} unidades, Faltan ${monto:.2f}'
        else:
            unidades = dif
            monto = unidades * p_venta
            estado = f'Sobran {unidades} unidades, Sobran ${monto:.2f}'

        filas += f'<tr><td>{nombre} (Última mod: {fecha})</td><td>{s_sis}</td><td>{s_real}</td><td>${p_costo:.2f}</td><td>${p_venta:.2f}</td><td>{estado}</td></tr>'

    tabla = f'''
    <table>
        <tr>
            <th>Producto</th><th>Stock sistema</th><th>Stock real</th><th>Precio costo</th><th>Precio venta</th><th>Diferencia</th>
        </tr>
        {filas}
    </table>
    <a href="/menu">Volver al menú</a>
    '''
    return page_template("Historial de Stock", tabla)

# ---EDITAR PRODUCTO---
@app.route('/editar', methods=['GET', 'POST'])
def editar():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    mensaje = ''
    producto = None

    if request.method == 'POST':
        if 'buscar' in request.form:
            nombre = request.form.get('nombre')
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("SELECT * FROM productos WHERE nombre = ?", (nombre,))
            producto = c.fetchone()
            conn.close()
            if not producto:
                mensaje = f'<p class="error">Producto "{nombre}" no encontrado.</p>'
        elif 'guardar' in request.form:
            id_prod = request.form.get('id')
            nombre = request.form.get('nombre')
            stock_sistema = int(request.form.get('stock_sistema'))
            stock_real = int(request.form.get('stock_real'))
            precio_costo = float(request.form.get('precio_costo'))
            precio_venta = float(request.form.get('precio_venta'))
            fecha_mod = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute('''UPDATE productos SET nombre=?, stock_sistema=?, stock_real=?, precio_costo=?, precio_venta=?, fecha_modificacion=? WHERE id=?''',
                      (nombre, stock_sistema, stock_real, precio_costo, precio_venta, fecha_mod, id_prod))
            conn.commit()
            conn.close()
            mensaje = '<p style="color:green;">✅ Producto actualizado correctamente.</p>'
            producto = (id_prod, nombre, stock_sistema, stock_real, precio_costo, precio_venta, fecha_mod)

    form_html = '''
    <form method="POST">
        Nombre del producto: <input type="text" name="nombre" required>
        <input type="submit" name="buscar" value="Buscar">
    </form>
    '''

    if producto:
        # La fecha de modificación del producto para mostrar en texto
        fecha_mod_str = producto[6] if producto[6] else ""

        form_html += f'''
        <form method="POST">
            <input type="hidden" name="id" value="{producto[0]}">
            Nombre producto: <input type="text" name="nombre" value="{producto[1]}" required><br>
            Stock sistema: <input type="number" name="stock_sistema" value="{producto[2]}" required><br>
            Stock real: <input type="number" name="stock_real" value="{producto[3]}" required><br>
            Precio costo: <input type="number" step="0.01" name="precio_costo" value="{producto[4]}" required><br>
            Precio venta: <input type="number" step="0.01" name="precio_venta" value="{producto[5]}" required><br>
            Fecha última modificación: 
            <input type="datetime-local" name="fecha_modificacion" id="fecha_modificacion" value="{fecha_mod_str.replace(' ', 'T')}" readonly><br>

            <input type="submit" name="guardar" value="Guardar cambios">
        </form>
        '''

    form_html += mensaje + '<a href="/menu">Volver al menú</a>'

    # Agregamos el script JS para que el campo fecha_modificacion se actualice en tiempo real (si querés que corra igual que en agregar)
    form_html += '''
    <script>
        function formatDateLocal(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            return `${year}-${month}-${day}T${hours}:${minutes}`;
        }

        function actualizarFechaHora() {
            const ahora = new Date();
            const formato = formatDateLocal(ahora);
            document.getElementById("fecha_modificacion").value = formato;
        }

        actualizarFechaHora();
        setInterval(actualizarFechaHora, 1000);
    </script>
    '''

    return page_template("Editar Producto", form_html)


# ---Elimina producto---
@app.route('/eliminar', methods=['GET', 'POST'])
def eliminar():
    if not session.get('logueado'):
        return redirect(url_for('login'))
    mensaje = ''
    producto = None

    if request.method == 'POST':
        if 'buscar' in request.form:
            nombre = request.form.get('nombre')
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("SELECT id, nombre FROM productos WHERE nombre = ?", (nombre,))
            producto = c.fetchone()
            conn.close()
            if not producto:
                mensaje = f'<p class="error">Producto "{nombre}" no encontrado.</p>'
        elif 'confirmar' in request.form:
            id_prod = request.form.get('id')
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("DELETE FROM productos WHERE id = ?", (id_prod,))
            conn.commit()
            conn.close()
            mensaje = '<p style="color:green;">✅ Producto eliminado correctamente.</p>'

    form_html = '''
    <form method="POST">
        Nombre del producto a eliminar: <input type="text" name="nombre" required>
        <input type="submit" name="buscar" value="Buscar">
    </form>
    '''

    if producto:
        form_html += f'''
        <p>¿Estás seguro que querés eliminar el producto <strong>{producto[1]}</strong>?</p>
        <form method="POST">
            <input type="hidden" name="id" value="{producto[0]}">
            <input type="submit" name="confirmar" value="Eliminar producto">
        </form>
        '''

    form_html += mensaje + '<a href="/menu">Volver al menú</a>'
    return page_template("Eliminar Producto", form_html)

fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    app.run(debug=True)
