from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import date

app = Flask(__name__)
app.secret_key = "clave_secreta_para_sesion"  # Requerido si usas flash messages

# Contraseña única para autorizar la eliminación de elementos
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
    
    cursor.execute("SELECT * FROM componentes")
    componentes = cursor.fetchall()

    cursor.execute("SELECT * FROM equipos_unicos")
    equipos = cursor.fetchall()
    
    consulta_prestamos = """
        SELECT p.id_prestamo, p.nombre_solicitante, p.rol_solicitante, 
               c.nombre AS componente_nom, c.numero_serie AS comp_sn,
               e.codigo_identificador AS equipo_cod, e.numero_serie AS equipo_sn,
               p.fecha_retiro, p.fecha_finalizacion, p.fecha_devolucion
        FROM prestamos p
        LEFT JOIN componentes c ON p.id_componente = c.id_componente
        LEFT JOIN equipos_unicos e ON p.id_equipo = e.id_equipo
        ORDER BY p.fecha_devolucion IS NOT NULL, p.fecha_retiro DESC
    """
    cursor.execute(consulta_prestamos)
    prestamos = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    return render_template('index.html', componentes=componentes, equipos=equipos, prestamos=prestamos)

@app.route('/nuevo_equipo', methods=['GET', 'POST'])
def nuevo_equipo():
    if request.method == 'POST':
        codigo = request.form['codigo']
        numero_serie = request.form.get('numero_serie') or None
        tipo = request.form['tipo']
        ubicacion = request.form['ubicacion']
        
        conexion = conectar_db()
        cursor = conexion.cursor()
        query = "INSERT INTO equipos_unicos (codigo_identificador, numero_serie, tipo, ubicacion) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (codigo, numero_serie, tipo, ubicacion))
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('index'))
    
    return render_template('nuevo_equipo.html')

@app.route('/nuevo_componente', methods=['GET', 'POST'])
def nuevo_componente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        numero_serie = request.form.get('numero_serie') or None
        descripcion = request.form['descripcion']
        stock = request.form['stock']
        
        conexion = conectar_db()
        cursor = conexion.cursor()
        query = "INSERT INTO componentes (nombre, numero_serie, descripcion, stock) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (nombre, numero_serie, descripcion, stock))
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('index'))
    
    return render_template('nuevo_componente.html')

@app.route('/eliminar_componente/<int:id_componente>', methods=['POST'])
def eliminar_componente(id_componente):
    password_ingresada = request.form.get('password')
    if password_ingresada == CLAVE_ELIMINACION:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM componentes WHERE id_componente = %s", (id_componente,))
        conexion.commit()
        cursor.close()
        conexion.close()
    return redirect(url_for('index'))

@app.route('/eliminar_equipo/<int:id_equipo>', methods=['POST'])
def eliminar_equipo(id_equipo):
    password_ingresada = request.form.get('password')
    if password_ingresada == CLAVE_ELIMINACION:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM equipos_unicos WHERE id_equipo = %s", (id_equipo,))
        conexion.commit()
        cursor.close()
        conexion.close()
    return redirect(url_for('index'))

@app.route('/nuevo_prestamo', methods=['GET', 'POST'])
def nuevo_prestamo():
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    
    if request.method == 'POST':
        nombre_solicitante = request.form['nombre_solicitante']
        rol = request.form['rol']
        fecha_ret = request.form['fecha_retiro']
        fecha_fin = request.form['fecha_finalizacion']
        id_equipo = request.form.get('id_equipo')
        
        query_insert_comp = "INSERT INTO prestamos (nombre_solicitante, rol_solicitante, id_componente, fecha_retiro, fecha_finalizacion) VALUES (%s, %s, %s, %s, %s)"
        query_stock = "UPDATE componentes SET stock = stock - %s WHERE id_componente = %s"
        
        for key, value in request.form.items():
            if key.startswith('cantidad_'):
                cantidad = int(value)
                if cantidad > 0:
                    id_comp = key.split('_')[1]
                    
                    cursor.execute("SELECT stock FROM componentes WHERE id_componente = %s", (id_comp,))
                    comp_db = cursor.fetchone()
                    
                    if comp_db and comp_db['stock'] >= cantidad:
                        for _ in range(cantidad):
                            cursor.execute(query_insert_comp, (nombre_solicitante, rol, id_comp, fecha_ret, fecha_fin))
                        cursor.execute(query_stock, (cantidad, id_comp))
        
        if id_equipo:
            query_insert_equipo = "INSERT INTO prestamos (nombre_solicitante, rol_solicitante, id_equipo, fecha_retiro, fecha_finalizacion) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query_insert_equipo, (nombre_solicitante, rol, id_equipo, fecha_ret, fecha_fin))
            cursor.execute("UPDATE equipos_unicos SET estado = 'Prestado' WHERE id_equipo = %s", (id_equipo,))
            
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('index'))
    else:
        cursor.execute("SELECT id_componente, nombre, numero_serie, stock FROM componentes WHERE stock > 0")
        componentes = cursor.fetchall()
        
        cursor.execute("SELECT id_equipo, codigo_identificador, numero_serie, ubicacion FROM equipos_unicos WHERE estado = 'Disponible'")
        equipos = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        return render_template('nuevo_prestamo.html', componentes=componentes, equipos=equipos)

@app.route('/devolver/<int:id_prestamo>', methods=['POST'])
def devolver(id_prestamo):
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    
    cursor.execute("SELECT id_componente, id_equipo FROM prestamos WHERE id_prestamo = %s", (id_prestamo,))
    prestamo = cursor.fetchone()
    
    if prestamo:
        hoy = date.today().strftime('%Y-%m-%d')
        cursor.execute("UPDATE prestamos SET fecha_devolucion = %s WHERE id_prestamo = %s", (hoy, id_prestamo))
        
        if prestamo['id_componente']:
            cursor.execute("UPDATE componentes SET stock = stock + 1 WHERE id_componente = %s", (prestamo['id_componente'],))
        
        if prestamo['id_equipo']:
            cursor.execute("UPDATE equipos_unicos SET estado = 'Disponible' WHERE id_equipo = %s", (prestamo['id_equipo'],))
        
        conexion.commit()

    cursor.close()
    conexion.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)