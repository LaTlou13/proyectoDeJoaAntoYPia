import io
import qrcode
from flask import Flask, render_template, request, redirect, url_for, send_file
import mysql.connector
from datetime import date
from urllib.parse import unquote

app = Flask(__name__)
app.secret_key = "clave_secreta_para_sesion"
CLAVE_ELIMINACION = "12345"

def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",         
        password="12345",  
        database="club_ciencias"
    )

@app.route('/')
def index():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    # 1. Obtener equipos
    cursor.execute("SELECT * FROM equipos_unicos")
    equipos = cursor.fetchall()

    # 2. Obtener componentes
    cursor.execute("SELECT * FROM componentes")
    componentes = cursor.fetchall()

    # 3. Obtener préstamos agrupados (Cabecera + Detalle)
    query_prestamos = """
        SELECT 
            p.id_prestamo,
            p.nombre_solicitante,
            p.rol_solicitante,
            p.fecha_retiro,
            p.fecha_finalizacion,
            p.fecha_devolucion,
            GROUP_CONCAT(
                CONCAT(
                    COALESCE(c.nombre, CONCAT('Equipo ', e.codigo_identificador)),
                    IF(dp.cantidad > 1, CONCAT(' (x', dp.cantidad, ')'), '')
                ) SEPARATOR ', '
            ) AS items_prestados
        FROM prestamos p
        JOIN detalle_prestamos dp ON p.id_prestamo = dp.id_prestamo
        LEFT JOIN componentes c ON dp.id_componente = c.id_componente
        LEFT JOIN equipos_unicos e ON dp.id_equipo = e.id_equipo
        GROUP BY p.id_prestamo
        ORDER BY p.fecha_devolucion IS NOT NULL, p.fecha_retiro DESC
    """
    cursor.execute(query_prestamos)
    prestamos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('index.html', equipos=equipos, componentes=componentes, prestamos=prestamos)

# --- RUTA DE CÓDIGO QR CORREGIDA ---
@app.route('/qr/<path:contenido>')
def generar_qr(contenido):
    try:
        # Decodifica el texto enviado por la URL y reconvierte el separador seguro a saltos de línea reales
        texto_limpio = unquote(contenido).replace(' | ', '\n')
        
        qr = qrcode.QRCode(
            version=None,  # Ajuste automático según texto
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=2,
        )
        
        qr.add_data(texto_limpio.encode('utf-8'))
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, 'PNG')
        buf.seek(0)

        return send_file(buf, mimetype='image/png')
    except Exception as e:
        print(f"Error al generar QR: {e}")
        return "Error al generar la imagen del código QR", 500

@app.route('/nuevo_equipo', methods=['GET', 'POST'])
def nuevo_equipo():
    if request.method == 'POST':
        codigo = request.form['codigo']
        numero_serie = request.form['numero_serie']
        tipo = request.form['tipo']

        conexion = conectar_db()
        cursor = conexion.cursor()
        
        # 1. Insertar el equipo
        cursor.execute(
            "INSERT INTO equipos_unicos (codigo_identificador, numero_serie, tipo) VALUES (%s, %s, %s)",
            (codigo, numero_serie, tipo)
        )
        id_equipo = cursor.lastrowid

        # 2. Asociar los componentes seleccionados con sus cantidades
        for key, value in request.form.items():
            if key.startswith('cant_comp_'):
                id_comp = key.replace('cant_comp_', '')
                try:
                    cantidad = int(value)
                    if cantidad > 0:
                        cursor.execute(
                            "INSERT INTO equipo_componentes (id_equipo, id_componente, cantidad) VALUES (%s, %s, %s)",
                            (id_equipo, id_comp, cantidad)
                        )
                        cursor.execute(
                            "UPDATE componentes SET stock = stock - %s WHERE id_componente = %s",
                            (cantidad, id_comp)
                        )
                except ValueError:
                    continue

        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('index'))

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM componentes WHERE stock > 0")
    componentes = cursor.fetchall()
    cursor.close()
    conexion.close()

    return render_template('nuevo_equipo.html', componentes=componentes)

@app.route('/nuevo_componente', methods=['GET', 'POST'])
def nuevo_componente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        tipo = request.form['tipo']
        numero_serie = request.form.get('numero_serie', None)
        stock_raw = request.form.get('stock', 1)
        
        try:
            stock = int(stock_raw)
        except ValueError:
            stock = 1

        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO componentes (nombre, tipo, numero_serie, stock) VALUES (%s, %s, %s, %s)",
            (nombre, tipo, numero_serie, stock)
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('index'))

    return render_template('nuevo_componente.html')

@app.route('/nuevo_prestamo', methods=['GET', 'POST'])
def nuevo_prestamo():
    # 1. Crear conexión y cursor usando tu función helper
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    if request.method == 'POST':
        nombre_solicitante = request.form.get('nombre_solicitante')
        rol_solicitante = request.form.get('rol_solicitante')
        fecha_retiro = request.form.get('fecha_retiro')
        fecha_finalizacion = request.form.get('fecha_finalizacion')
        id_equipo = request.form.get('id_equipo')

        # Insertar cabecera del préstamo
        query_prestamo = """
            INSERT INTO prestamos (nombre_solicitante, rol_solicitante, fecha_retiro, fecha_finalizacion)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query_prestamo, (nombre_solicitante, rol_solicitante, fecha_retiro, fecha_finalizacion))
        id_prestamo = cursor.lastrowid

        # Insertar equipo si fue seleccionado
        if id_equipo and id_equipo.strip() != "":
            query_det_equipo = """
                INSERT INTO detalle_prestamos (id_prestamo, id_equipo, cantidad)
                VALUES (%s, %s, 1)
            """
            cursor.execute(query_det_equipo, (id_prestamo, id_equipo))

        # Recorrer componentes seleccionados y actualizar stock
        for key, value in request.form.items():
            if key.startswith('cantidad_'):
                id_comp = key.replace('cantidad_', '')
                try:
                    cantidad = int(value)
                    if cantidad > 0:
                        query_det_comp = """
                            INSERT INTO detalle_prestamos (id_prestamo, id_componente, cantidad)
                            VALUES (%s, %s, %s)
                        """
                        cursor.execute(query_det_comp, (id_prestamo, id_comp, cantidad))

                        query_stock = "UPDATE componentes SET stock = stock - %s WHERE id_componente = %s"
                        cursor.execute(query_stock, (cantidad, id_comp))
                except ValueError:
                    continue

        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('index'))

    # Método GET: Consultar los items para el formulario
    cursor.execute("SELECT * FROM componentes WHERE stock > 0")
    componentes = cursor.fetchall()

    cursor.execute("SELECT * FROM equipos_unicos")
    equipos = cursor.fetchall()

    cursor.close()
    conexion.close()
    return render_template('nuevo_prestamo.html', componentes=componentes, equipos=equipos)

@app.route('/devolver/<int:id_prestamo>', methods=['POST'])
def devolver(id_prestamo):
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    fecha_hoy = date.today().strftime('%Y-%m-%d')

    # 1. Reponer el stock de los componentes involucrados
    query_items = "SELECT id_componente, cantidad FROM detalle_prestamos WHERE id_prestamo = %s AND id_componente IS NOT NULL"
    cursor.execute(query_items, (id_prestamo,))
    items = cursor.fetchall()

    for item in items:
        query_restaurar = "UPDATE componentes SET stock = stock + %s WHERE id_componente = %s"
        cursor.execute(query_restaurar, (item['cantidad'], item['id_componente']))

    # 2. Marcar el préstamo como devuelto
    query_devolucion = "UPDATE prestamos SET fecha_devolucion = %s WHERE id_prestamo = %s"
    cursor.execute(query_devolucion, (fecha_hoy, id_prestamo))

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect(url_for('index'))

@app.route('/editar_stock/<int:id_componente>', methods=['POST'])
def editar_stock(id_componente):
    clave_ingresada = request.form.get('clave', '').strip()
    if clave_ingresada != CLAVE_ELIMINACION:
        return "<script>alert('Contraseña incorrecta. No se modificó el stock.'); window.location.href='/';</script>"

    stock_raw = request.form.get('stock', '').strip()

    if not stock_raw:
        return "<script>alert('El campo stock no puede estar vacío.'); window.location.href='/';</script>"

    try:
        nuevo_stock = int(stock_raw)
    except ValueError:
        return "<script>alert('El stock ingresado debe ser un número entero.'); window.location.href='/';</script>"

    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("UPDATE componentes SET stock = %s WHERE id_componente = %s", (nuevo_stock, id_componente))
    conexion.commit()
    cursor.close()
    conexion.close()
    return redirect(url_for('index'))

@app.route('/editar_componente/<int:id_componente>', methods=['POST'])
def editar_componente(id_componente):
    clave_ingresada = request.form.get('clave', '').strip()
    if clave_ingresada != CLAVE_ELIMINACION:
        return "<script>alert('Contraseña incorrecta. No se modificó el componente.'); window.location.href='/';</script>"

    nombre = request.form.get('nombre')
    tipo = request.form.get('tipo')
    numero_serie = request.form.get('numero_serie')
    descripcion = request.form.get('descripcion')
    stock_raw = request.form.get('stock', '').strip()

    try:
        stock = int(stock_raw)
    except ValueError:
        return "<script>alert('El valor de stock debe ser un número entero.'); window.location.href='/';</script>"

    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE componentes 
        SET nombre = %s, tipo = %s, numero_serie = %s, descripcion = %s, stock = %s 
        WHERE id_componente = %s
    """, (nombre, tipo, numero_serie, descripcion, stock, id_componente))
    
    conexion.commit()
    cursor.close()
    conexion.close()
    return redirect(url_for('index'))

@app.route('/editar_equipo/<int:id_equipo>', methods=['POST'])
def editar_equipo(id_equipo):
    clave_ingresada = request.form.get('clave', '').strip()
    if clave_ingresada != CLAVE_ELIMINACION:
        return "<script>alert('Contraseña incorrecta. No se modificó el equipo.'); window.location.href='/';</script>"

    codigo = request.form.get('codigo')
    numero_serie = request.form.get('numero_serie')
    tipo = request.form.get('tipo')

    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE equipos_unicos 
        SET codigo_identificador = %s, numero_serie = %s, tipo = %s 
        WHERE id_equipo = %s
    """, (codigo, numero_serie, tipo, id_equipo))

    conexion.commit()
    cursor.close()
    conexion.close()
    return redirect(url_for('index'))

@app.route('/eliminar_equipo/<int:id_equipo>', methods=['POST'])
def eliminar_equipo(id_equipo):
    clave_ingresada = request.form.get('clave', '').strip()

    if clave_ingresada != CLAVE_ELIMINACION:
        return "<script>alert('Contraseña incorrecta. No se eliminó el equipo.'); window.location.href='/';</script>"

    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id_componente, cantidad FROM equipo_componentes WHERE id_equipo = %s", 
            (id_equipo,)
        )
        componentes_equipo = cursor.fetchall()
        for comp in componentes_equipo:
            cursor.execute(
                "UPDATE componentes SET stock = stock + %s WHERE id_componente = %s",
                (comp['cantidad'], comp['id_componente'])
            )

        cursor.execute("DELETE FROM equipo_componentes WHERE id_equipo = %s", (id_equipo,))
        cursor.execute("DELETE FROM detalle_prestamos WHERE id_equipo = %s", (id_equipo,))
        cursor.execute("UPDATE prestamos SET id_equipo = NULL WHERE id_equipo = %s", (id_equipo,))

        cursor.execute("DELETE FROM equipos_unicos WHERE id_equipo = %s", (id_equipo,))

        conexion.commit()
    except mysql.connector.Error as err:
        conexion.rollback()
        print(f"Error al eliminar equipo: {err}")
    finally:
        cursor.close()
        conexion.close()

    return redirect(url_for('index'))

@app.route('/eliminar_componente/<int:id_componente>', methods=['POST'])
def eliminar_componente(id_componente):
    clave_ingresada = request.form.get('clave', '').strip()

    if clave_ingresada != CLAVE_ELIMINACION:
        return "<script>alert('Contraseña incorrecta. No se eliminó el componente.'); window.location.href='/';</script>"

    conexion = conectar_db()
    cursor = conexion.cursor()

    try:
        cursor.execute("DELETE FROM detalle_prestamos WHERE id_componente = %s", (id_componente,))
        cursor.execute("DELETE FROM equipo_componentes WHERE id_componente = %s", (id_componente,))
        cursor.execute("DELETE FROM componentes WHERE id_componente = %s", (id_componente,))

        conexion.commit()
    except mysql.connector.Error as err:
        conexion.rollback()
        print(f"Error al eliminar componente: {err}")
    finally:
        cursor.close()
        conexion.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)