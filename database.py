import sqlite3
from datetime import datetime
import os

class BaseDatos:
    def __init__(self,db_name="punto_de_venta.db"):
                # Seccion para cambiar la ruta de guardado en la base de datos 
                #data_path = os.getenv('APPDATA')

                #if not data_path:
                    #data_path = os.path.expanduser('~')

                #carpeta_pos = os.path.join(data_path, "PosRegalos")
                #os.makedirs(carpeta_pos, exist_ok=True)

                #self.db_path = os.path.join(carpeta_pos, db_name)
                #-----------------------------------------------------
                self.conn = sqlite3.connect(db_name) # cambiar db_name por self.db_path para hacer el cambio de ruta para la base de datos 
                self.conn.row_factory = sqlite3.Row
                self.cursor = self.conn.cursor()


    def iniciar_db(self):

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                codigo TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                descripcion TEXT DEFAULT 'Sin descripción',
                precio REAL NOT NULL,
                stock INTEGER NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_prod TEXT,
                fecha_hora TEXT NOT NULL,
                total REAL NOT NULL,
                pago REAL NOT NULL,
                cambio REAL NOT NULL,
                metodo_pago TEXT NOT NULL DEFAULT 'Efectivo',
                FOREIGN KEY (codigo_prod) REFERENCES productos(codigo)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                codigo TEXT NOT NULL,
                nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS apartados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL,
                fecha_liquidacion TEXT,
                total REAL NOT NULL,
                a_cuenta REAL NOT NULL,
                resta REAL NOT NULL,
                estado TEXT DEFAULT 'Pendiente'
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalle_apartados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                apartado_id INTEGER NOT NULL,
                codigo TEXT NOT NULL,
                nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (apartado_id) REFERENCES apartados(id)
            )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS caja_diaria (
            fecha TEXT PRIMARY KEY,
            fondo_inicial REAL NOT NULL
            )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS retiros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_hora TEXT NOT NULL,
        monto REAL NOT NULL,
        concepto TEXT
        )
    ''')

        self.conn.commit()

    def obtener_producto(self, codigo):
        self.cursor.execute("SELECT nombre,precio,stock FROM productos WHERE codigo = ?", (codigo,))
        return self.cursor.fetchone()

    def obtener_todos_productos(self):
        self.cursor.execute ("SELECT * FROM productos")
        return self.cursor.fetchall()

    def guardar_productos(self,cod, nom, des, pre, sto):

        try:
            self.cursor.execute("INSERT INTO productos VALUES (?, ?, ?, ?, ?)", 
                                (cod, nom, des, pre, sto))
            self.conn.commit()
            return True,"Producto registrado correctamente "
        
        except sqlite3.IntegrityError:

            return False, "Error ya existe un producto registrado con ese codigo de barras"
        
        except ValueError:

            return False, "Error el precio y stock deben ser valores numéricos válidos."

    def descontar_stock(self,codigo,datos):
        self.cursor.execute("UPDATE productos SET stock = stock - ? WHERE codigo = ?", (datos['cant'], codigo))
        self.conn.commit()

    def borrar_productos(self,codigo):
        self.cursor.execute("DELETE FROM productos WHERE codigo =?",(codigo,))
        self.conn.commit()

    def registrar_venta(self, carrito, codigo_prod, total, pago, cambio, metodo_pago='Efectivo'):
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Registrar encabezado de la venta
        self.cursor.execute(
            "INSERT INTO ventas (codigo_prod,fecha_hora, total, pago, cambio, metodo_pago) VALUES (? ,?, ?, ?, ?, ?)",
            (codigo_prod ,fecha_actual, total, pago, cambio, metodo_pago)
        )
        venta_id = self.cursor.lastrowid # Recupera el ID de la venta recién creada
        
        # Registrar el detalle de producto
        for codigo, datos in carrito.items():
            subtotal = datos['cant'] * datos['precio']
            self.cursor.execute("""
                INSERT INTO detalle_ventas (venta_id, codigo, nombre, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (venta_id, codigo, datos['nombre'], datos['cant'], datos['precio'], subtotal))
        
        self.conn.commit()
        return venta_id

    def obtener_ventas_por_fecha(self, fecha):
        # Seleccionamos metodo de pago
        self.cursor.execute("""
            SELECT id,codigo_prod ,fecha_hora, total, pago, cambio, metodo_pago 
            FROM ventas 
            WHERE fecha_hora LIKE ? 
            ORDER BY fecha_hora DESC
        """, (f"{fecha}%",))
        return self.cursor.fetchall()

    def obtener_totales_por_metodo(self, fecha):
        self.cursor.execute("""
            SELECT metodo_pago, SUM(total) as total_vendido
            FROM ventas 
            WHERE fecha_hora LIKE ? 
            GROUP BY metodo_pago
        """, (f"{fecha}%",))
        return self.cursor.fetchall()

    def obtener_detalle_venta(self, venta_id):
        self.cursor.execute("""
            SELECT codigo, nombre, cantidad, precio_unitario, subtotal 
            FROM detalle_ventas 
            WHERE venta_id = ?
        """, (venta_id,))
        return self.cursor.fetchall()

    # Sistema de apartado
    def registrar_apartado(self, cliente, carrito, total, a_cuenta):
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resta = total - a_cuenta
        estado = 'Liquidado' if resta <= 0 else 'Pendiente'
        fecha_liq = fecha_actual if estado == 'Liquidado' else "---"
        
        # Crear el registro del apartado
        self.cursor.execute("""
            INSERT INTO apartados (cliente, fecha_creacion, fecha_liquidacion, total, a_cuenta, resta, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cliente, fecha_actual, fecha_liq, total, a_cuenta, resta, estado))
        
        apartado_id = self.cursor.lastrowid
        
        # Guardar el detalle de productos apartados
        for codigo, datos in carrito.items():
            subtotal = datos['cant'] * datos['precio']
            self.cursor.execute("""
                INSERT INTO detalle_apartados (apartado_id, codigo, nombre, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (apartado_id, codigo, datos['nombre'], datos['cant'], datos['precio'], subtotal))

        # Registrar anticipo como venta del dia
        if a_cuenta > 0:
            self.cursor.execute("""
                INSERT INTO ventas (fecha_hora, total, pago, cambio, metodo_pago)
                VALUES (?, ?, ?, 0.0, 'Efectivo')
            """, (fecha_actual, a_cuenta, a_cuenta))
            
            venta_id = self.cursor.lastrowid
            
            self.cursor.execute("""
                INSERT INTO detalle_ventas (venta_id, codigo, nombre, cantidad, precio_unitario, subtotal)
                VALUES (?, 'APARTADO', ?, 1, ?, ?)
            """, (venta_id, f"Anticipo Apartado #{apartado_id} ({cliente})", a_cuenta, a_cuenta))
            
        self.conn.commit()
        return apartado_id

    def abonar_a_apartado(self, apartado_id, monto_abono):
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.cursor.execute("SELECT cliente, a_cuenta, resta FROM apartados WHERE id = ?", (apartado_id,))
        row = self.cursor.fetchone()

        if not row:
            raise ValueError(f"No se encontró el apartado con ID {apartado_id}")
            
        cliente = row['cliente']
        nuevo_a_cuenta = row['a_cuenta'] + monto_abono
        nueva_resta = row['resta'] - monto_abono
        
        estado = 'Liquidado' if nueva_resta <= 0 else 'Pendiente'
        fecha_liq = fecha_actual if estado == 'Liquidado' else "---"
        
        # Actualizar el estado del apartado
        self.cursor.execute("""
            UPDATE apartados 
            SET a_cuenta = ?, resta = ?, estado = ?, fecha_liquidacion = ?
            WHERE id = ?
        """, (nuevo_a_cuenta, nueva_resta, estado, fecha_liq, apartado_id))

        # Registrar el abono actual
        self.cursor.execute("""
            INSERT INTO ventas (fecha_hora, total, pago, cambio, metodo_pago)
            VALUES (?, ?, ?, 0.0, 'Efectivo')
        """, (fecha_actual, monto_abono, monto_abono))
        
        venta_id = self.cursor.lastrowid

        self.cursor.execute("""
            INSERT INTO detalle_ventas (venta_id, codigo, nombre, cantidad, precio_unitario, subtotal)
            VALUES (?, 'ABONO', ?, 1, ?, ?)
        """, (venta_id, f"Abono Apartado #{apartado_id} ({cliente})", monto_abono, monto_abono))
        
        self.conn.commit()
        
        return estado, nueva_resta        
    def obtener_todos_apartados(self):
        self.cursor.execute("""
            SELECT id, cliente, fecha_creacion, fecha_liquidacion, total, a_cuenta, resta, estado 
            FROM apartados 
            ORDER BY estado DESC, fecha_creacion ASC
        """)
        return self.cursor.fetchall()

    def actualizar_producto(self, codigo, nombre, descripcion, precio, stock):

        self.cursor.execute("""
            UPDATE productos 
            SET nombre = ?, descripcion = ?, precio = ?, stock = ? 
            WHERE codigo = ?
        """, (nombre, descripcion, precio, stock, codigo))
        self.conn.commit()

    def buscar_productos(self, texto):

        param = f"%{texto}%"
        self.cursor.execute(
            "SELECT codigo, nombre, precio, stock FROM productos WHERE codigo LIKE ? OR nombre LIKE ?",
            (param, param)
        )
        return self.cursor.fetchall()

    def obtener_fondo_caja(self, fecha):

        self.cursor.execute("SELECT fondo_inicial FROM caja_diaria WHERE fecha = ?", (fecha,))
        row = self.cursor.fetchone()
        return row[0] if row else 0.0

    def guardar_fondo_caja(self, fecha, monto):

        self.cursor.execute("""
            INSERT INTO caja_diaria (fecha, fondo_inicial) 
            VALUES (?, ?)
            ON CONFLICT(fecha) DO UPDATE SET fondo_inicial = excluded.fondo_inicial
        """, (fecha, monto))
        self.conn.commit()

    def registrar_retiro(self, monto, concepto="Retiro de caja"):
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
            "INSERT INTO retiros (fecha_hora, monto, concepto) VALUES (?, ?, ?)",
            (fecha_actual, monto, concepto)
            )
            self.conn.commit()

    def obtener_total_retiros(self, fecha):
        self.cursor.execute(
            "SELECT SUM(monto) FROM retiros WHERE fecha_hora LIKE ?",
            (f"{fecha}%",)
        )
        row = self.cursor.fetchone()
        return row[0] if row[0] else 0.0

    def obtener_ultimo_saldo_final(self, fecha_actual):

        self.cursor.execute("SELECT fecha FROM caja_diaria WHERE fecha < ? ORDER BY fecha DESC LIMIT 1", (fecha_actual,))
        row = self.cursor.fetchone()
        
        if row:
            fecha_ant = row[0]
            fondo_ant = self.obtener_fondo_caja(fecha_ant)
            
            # Ventas en efectivo del día
            self.cursor.execute("SELECT SUM(total) FROM ventas WHERE fecha_hora LIKE ? AND metodo_pago = 'Efectivo'", (f"{fecha_ant}%",))
            v_row = self.cursor.fetchone()
            ventas_ant = v_row[0] if v_row and v_row[0] else 0.0
            
            # Retiros del dia
            self.cursor.execute("SELECT SUM(monto) FROM retiros WHERE fecha_hora LIKE ?", (f"{fecha_ant}%",))
            r_row = self.cursor.fetchone()
            retiros_ant = r_row[0] if r_row and r_row[0] else 0.0
            
            # Retorna el cálculo matemático del saldo final anterior
            return fondo_ant + ventas_ant - retiros_ant
            
        return 0.0 # Si no hay días anteriores, devuelve 0