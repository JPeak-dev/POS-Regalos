import tkinter as tk
from tkinter import ttk, messagebox
from database import BaseDatos
import datetime

class Interfaz:
    
    def __init__(self,root):
        #Configuracón de la ventana raiz
        self.root = root
        self.root.title("Punto de venta tienda de regalos")
        self.root.state('zoomed')
        self.root.configure(bg="#f1f5f9")

        # Estilos visuales
        self.configurar_estilos()

        #Variables globales 
        self.total_venta = 0.0
        self.carrito = {} 

        #Instancia de la base de datos
        self.bd = BaseDatos()

        # Construir Interfaz
        self.crear_header()
        self.crear_layout_principal()
        
        self.entry_codigo.focus_set()

    def configurar_estilos(self):
            self.style = ttk.Style()
            self.style.theme_use("alt")
    
            # Colores genereales 
            self.style.configure(".", background="#f1f5f9", font=("Segoe UI", 10))
            self.style.configure("Treeview", 
                                font=("Segoe UI", 11), 
                                rowheight=30, 
                                background="#ffffff",
                                fieldbackground="#ffffff")
            self.style.configure("Treeview.Heading", 
                                font=("Segoe UI", 11, "bold"), 
                                background="#0f172a", 
                                foreground="#ffffff")
            self.style.map("Treeview", background=[('selected', '#3b82f6')])

    #Header de la ventana pricnipal

    def crear_header(self):
        header_frame = tk.Frame(self.root, bg="#0f172a", height=60)
        header_frame.pack(fill="x", side="top")

        titulo = tk.Label(header_frame, text="🎁 La casa del regalo", font=("Segoe UI", 18, "bold"), fg="#ffffff", bg="#0f172a")
        titulo.pack(side="left", padx=20, pady=12)

        btn_mostrar_inv = tk.Button(header_frame,text="Mostrar inventario",font=("Segoe UI", 10, "bold"),
                                    bg="#3b82f6",fg="white",activebackground="#2563eb",activeforeground="white",
                                    bd=2, padx=0, pady=0,cursor="hand2", command=self.mostrar_inventario)
        btn_mostrar_inv.pack(side="right",padx=10,)

        btn_reportes = tk.Button(header_frame, text="📊 Ventas del Día", font=("Segoe UI", 10, "bold"),
                                bg="#10b981", fg="white", activebackground="#059669", activeforeground="white",
                                bd=2, padx=10, pady=0, cursor="hand2", command=self.abrir_ventana_reportes)
        btn_reportes.pack(side="right", padx=10)

        btn_apartados = tk.Button(header_frame, text="📦 Gestión de Apartados", font=("Segoe UI", 10, "bold"),
                                bg="#f59e0b", fg="white", activebackground="#d97706", activeforeground="white",
                                bd=2, padx=10, pady=0, cursor="hand2", command=self.abrir_ventana_apartados)
        btn_apartados.pack(side="right", padx=10)

    def crear_layout_principal(self):
        main_container = tk.Frame(self.root, bg="#f1f5f9")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Panel izquierdo de venta de la ventana principal
        left_panel = tk.Frame(main_container, bg="#f1f5f9")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Campos para ingresar o escanear el codigo de barras
        scan_frame = tk.Frame(left_panel, bg="#ffffff", bd=1, relief="solid", padx=10, pady=10)
        scan_frame.pack(fill="x", pady=(0, 15))

        lbl_escaneo = tk.Label(scan_frame, text="Escanea código o presiona Enter:", font=("Segoe UI", 11, "bold"), bg="#ffffff", fg="#334155")
        lbl_escaneo.pack(anchor="w")

        self.entry_codigo = tk.Entry(scan_frame, font=("Segoe UI", 14), bd=1, relief="solid")
        self.entry_codigo.pack(fill="x", pady=(5, 0))

        # Codigo de barras al usar scanner
        self.entry_codigo.bind("<Return>", self.agregar_producto_carrito)

        # Tabla de Productos Agregados
        table_frame = tk.Frame(left_panel, bg="#ffffff")
        table_frame.pack(fill="both", expand=True)

        columns = ("codigo", "nombre", "precio", "cant", "subtotal")
        self.tabla = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tabla.heading("codigo", text="Código")
        self.tabla.heading("nombre", text="Producto")
        self.tabla.heading("precio", text="Precio U.")
        self.tabla.heading("cant", text="Cant.")
        self.tabla.heading("subtotal", text="Subtotal")

        self.tabla.column("codigo", width=120, anchor="center")
        self.tabla.column("nombre", width=250, anchor="w")
        self.tabla.column("precio", width=100, anchor="e")
        self.tabla.column("cant", width=80, anchor="center")
        self.tabla.column("subtotal", width=120, anchor="e")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)

        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # panel derecho con el resumen de productos
        right_panel = tk.Frame(main_container, bg="#ffffff", bd=1, relief="solid", padx=20, pady=20)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)
        right_panel.config(width=340)

        # Indicador de Total
        lbl_total_title = tk.Label(right_panel, text="TOTAL A PAGAR", font=("Segoe UI", 12, "bold"), fg="#64748b", bg="#ffffff")
        lbl_total_title.pack(anchor="w")

        self.lbl_total_val = tk.Label(right_panel, text="$0.00", font=("Segoe UI", 32, "bold"), fg="#16a34a", bg="#ffffff")
        self.lbl_total_val.pack(anchor="w", pady=(0, 20))

        self.metodo_pago_var = tk.StringVar(value="Efectivo")
        lbl_metodo = tk.Label(right_panel, text="Método de Pago:", font=("Segoe UI", 11, "bold"), bg="#ffffff", fg="#334155")
        lbl_metodo.pack(anchor="w", pady=(5, 0))

        combo_metodo = ttk.Combobox(right_panel, textvariable=self.metodo_pago_var, values=["Efectivo", "Tarjeta"], state="readonly", font=("Segoe UI", 12))
        combo_metodo.pack(fill="x", pady=(0, 10))
        combo_metodo.bind("<<ComboboxSelected>>", self.al_cambiar_metodo)

        # Sección de Cobro (Efectivo y Cambio)
        lbl_pago = tk.Label(right_panel, text="Efectivo Recibido ($):", font=("Segoe UI", 11, "bold"), bg="#ffffff", fg="#334155")
        lbl_pago.pack(anchor="w")

        self.entry_pago = tk.Entry(right_panel, font=("Segoe UI", 14), bd=1, relief="solid")
        self.entry_pago.pack(fill="x", pady=(5, 10))
        self.entry_pago.bind("<KeyRelease>", self.calcular_cambio)

        lbl_cambio_title = tk.Label(right_panel, text="Cambio a Entregar:", font=("Segoe UI", 11, "bold"), bg="#ffffff", fg="#334155")
        lbl_cambio_title.pack(anchor="w")

        self.lbl_cambio_val = tk.Label(right_panel, text="$0.00", font=("Segoe UI", 20, "bold"), fg="#2563eb", bg="#ffffff")
        self.lbl_cambio_val.pack(anchor="w", pady=(0, 20))

        # Botones de Acción
        btn_cobrar = tk.Button(right_panel, text="✔ COBRAR (ENTER)", font=("Segoe UI", 12, "bold"),
                            bg="#16a34a", fg="white", activebackground="#15803d", activeforeground="white",
                            bd=0, pady=12, cursor="hand2", command=self.procesar_cobro)
        btn_cobrar.pack(fill="x", pady=(0, 10))

        btn_apartar = tk.Button(right_panel, text="📦 APARTAR PRODUCTOS", font=("Segoe UI", 11, "bold"),
                                bg="#f59e0b", fg="white", activebackground="#d97706", activeforeground="white",
                                bd=0, pady=10, cursor="hand2", command=self.dialogo_crear_apartado)
        btn_apartar.pack(fill="x", pady=(0, 10))

        btn_quitar = tk.Button(right_panel, text="🗑 Quitar Elemento", font=("Segoe UI", 10),
                            bg="#ef4444", fg="white", activebackground="#dc2626", activeforeground="white",
                            bd=0, pady=8, cursor="hand2", command=self.quitar_elemento_carrito)
        btn_quitar.pack(fill="x", pady=(0, 10))

        btn_cancelar = tk.Button(right_panel, text="❌ Cancelar Venta", font=("Segoe UI", 10),
                                bg="#94a3b8", fg="white", activebackground="#64748b", activeforeground="white",
                                bd=0, pady=8, cursor="hand2", command=self.limpiar_venta)
        btn_cancelar.pack(fill="x")

    def agregar_producto_carrito(self, event=None):
        codigo = self.entry_codigo.get().strip()
        self.entry_codigo.delete(0, tk.END)

        if not codigo:
            return

        prod = self.bd.obtener_producto(codigo)

        if prod:
            nombre, precio, stock = prod
            cant_actual = self.carrito[codigo]['cant'] if codigo in self.carrito else 0

            if cant_actual + 1 > stock:
                messagebox.showwarning("Stock Insuficiente", f"Solo quedan {stock} unidades de '{nombre}'.")
            else:
                if codigo in self.carrito:
                    self.carrito[codigo]['cant'] += 1
                else:
                    self.carrito[codigo] = {'nombre': nombre, 'precio': precio, 'cant': 1, 'stock': stock}
                
                self.actualizar_tabla()
        else:
            messagebox.showerror("No encontrado", f"El código '{codigo}' no está registrado en el sistema.")

        self.entry_codigo.focus_set()

    def actualizar_tabla(self):
        # Limpiar tabla
        for row in self.tabla.get_children():
            self.tabla.delete(row)

        self.total_venta = 0.0

        for codigo, datos in self.carrito.items():
            subtotal = datos['precio'] * datos['cant']
            self.total_venta += subtotal
            self.tabla.insert("", "end", values=(
                codigo, 
                datos['nombre'], 
                f"${datos['precio']:.2f}", 
                datos['cant'], 
                f"${subtotal:.2f}"
            ))

        self.lbl_total_val.config(text=f"${self.total_venta:.2f}")

        if hasattr(self, 'metodo_pago_var') and self.metodo_pago_var.get() == "Tarjeta":
            self.entry_pago.config(state="normal")
            self.entry_pago.delete(0, tk.END)
            self.entry_pago.insert(0, str(self.total_venta))
            self.entry_pago.config(state="disabled")

        self.calcular_cambio()

    def calcular_cambio(self, event=None):
        try:
            pago = float(self.entry_pago.get().strip())
            cambio = pago - self.total_venta
            if cambio >= 0:
                self.lbl_cambio_val.config(text=f"${cambio:.2f}", fg="#16a34a")
            else:
                self.lbl_cambio_val.config(text="Insuficiente", fg="#ef4444")
        except ValueError:
            self.lbl_cambio_val.config(text="$0.00", fg="#2563eb")

    def al_cambiar_metodo(self, event=None):
        if self.metodo_pago_var.get() == "Tarjeta":
            # Si es tarjeta, el pago es exacto y no hay cambio
            self.entry_pago.config(state="normal")
            self.entry_pago.delete(0, tk.END)
            self.entry_pago.insert(0, str(self.total_venta))
            self.entry_pago.config(state="disabled")
            self.lbl_cambio_val.config(text="$0.00", fg="#16a34a")
        else:
            # Si es efectivo habilitar campo para escribir
            self.entry_pago.config(state="normal")
            self.entry_pago.delete(0, tk.END)
            self.lbl_cambio_val.config(text="$0.00", fg="#2563eb")

    def quitar_elemento_carrito(self):
        selected_item = self.tabla.selection()
        if not selected_item:
            messagebox.showinfo("Atención", "Selecciona un producto de la lista para eliminarlo.")
            return

        item_values = self.tabla.item(selected_item)['values']
        codigo = str(item_values[0])

        if codigo in self.carrito:
            if self.carrito[codigo]['cant'] > 1:
                self.carrito[codigo]['cant'] -= 1
            else:
                del self.carrito[codigo]

        self.actualizar_tabla()
        self.entry_codigo.focus_set()

    def procesar_cobro(self):
        if not self.carrito:
            messagebox.showwarning("Venta Vacía", "No hay productos en la lista de venta.")
            return

        metodo = self.metodo_pago_var.get()

        try:
            if metodo == "Tarjeta":
                pago = self.total_venta
            else:
                pago = float(self.entry_pago.get().strip()) if self.entry_pago.get() else 0.0
                
            if pago < self.total_venta:
                messagebox.showerror("Pago Insuficiente", "El monto ingresado es menor al total.")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingresa un monto válido en el pago.")
            return

        # Descontar del inventario en SQLite
        for codigo, datos in self.carrito.items():
            self.bd.descontar_stock(codigo, datos)

        cambio = pago - self.total_venta
        
        id_venta = self.bd.registrar_venta(self.carrito, self.total_venta, pago, cambio, metodo)

        messagebox.showinfo("Venta Exitosa", f"Venta registrada con éxito.\n\nMétodo: {metodo}\nTotal: ${self.total_venta:.2f}\nCambio: ${cambio:.2f}")

        self.limpiar_venta()
        
        # Restaurar método a efectivo por defecto
        self.metodo_pago_var.set("Efectivo")
        self.al_cambiar_metodo()

    def limpiar_venta(self):
        self.carrito.clear()
        self.entry_pago.delete(0, tk.END)
        self.actualizar_tabla()
        self.entry_codigo.focus_set()


    def abrir_ventana_productos(self):
        win = tk.Toplevel(self.root)
        win.title("Gestión de Productos")
        win.geometry("450x380")
        win.configure(bg="#ffffff")
        win.grab_set() 

        tk.Label(win, text="Registrar Nuevo Producto", font=("Segoe UI", 14, "bold"), bg="#ffffff", fg="#0f172a").pack(pady=15)

        form_frame = tk.Frame(win, bg="#ffffff", padx=20)
        form_frame.pack(fill="both", expand=True)

        fields = [
            ("Código de Barras:", "ent_cod"),
            ("Nombre del Producto:", "ent_nom"),
            ("Descripción del producto:","ent_des"),
            ("Precio de Venta ($):", "ent_pre"),
            ("Stock Inicial:", "ent_sto")
        ]

        entries = {}
        for idx, (label_text, var_name) in enumerate(fields):
            tk.Label(form_frame, text=label_text, font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#334155").grid(row=idx*2, column=0, sticky="w", pady=(5,0))
            ent = tk.Entry(form_frame, font=("Segoe UI", 11), bd=1, relief="solid")
            ent.grid(row=idx*2+1, column=0, sticky="ew", pady=(0, 10))
            entries[var_name] = ent

        form_frame.grid_columnconfigure(0, weight=1)

        def guardar():
            cod = entries['ent_cod'].get().strip()
            nom = entries['ent_nom'].get().strip()
            des = entries['ent_des'].get().strip()
            pre = entries['ent_pre'].get().strip()
            sto = entries['ent_sto'].get().strip()

            if not (cod and nom and pre and sto):
                messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=win)
                return

            try:
                pre_val = float(pre)
                sto_val = int(sto)
            except ValueError:
                messagebox.showerror("Error", "El precio y stock deben ser valores numéricos válidos.", parent=win)
                return
            
            exito, mensaje = self.bd.guardar_productos(cod, nom, des, pre_val, sto_val)

            if exito:
                messagebox.showinfo("Éxito", f"Producto '{nom}' registrado correctamente.", parent=win)
                win.destroy()
                self.entry_codigo.focus_set()
                self.cargar_tabla_inventario(self.bd.obtener_todos_productos())
            else:
                messagebox.showerror("Error", mensaje, parent=win)

        btn_guardar = tk.Button(win, text="Guardar Producto", font=("Segoe UI", 11, "bold"),
                                bg="#3b82f6", fg="white", bd=0, pady=8, cursor="hand2", command=guardar)
        btn_guardar.pack(fill="x", padx=20, pady=20)

    def mostrar_inventario(self):
        self.ventana = tk.Toplevel(self.root)
        self.ventana.title("Inventario")
        self.ventana.state('zoomed')
        self.ventana.configure(bg="#ffffff")
        self.ventana.grab_set()

        header_frame = tk.Frame(self.ventana, bg="#0f172a", height=60)
        header_frame.pack(fill="x", side="top")

        tk.Label(header_frame, text="Inventario", font=("Segoe UI", 14, "bold"), bg="#0f172a", fg="#ffffff").pack(padx=12, pady=20,side="left")

        btn_inventario = tk.Button(header_frame, text="➕ Agregar producto", font=("Segoe UI", 10, "bold"),
                                    bg="#3b82f6", fg="white", activebackground="#2563eb", activeforeground="white",
                                    bd=2, padx=15, pady=6, cursor="hand2",command=self.abrir_ventana_productos)
        btn_inventario.pack(side="right", padx=10)

        form_frame = tk.Frame(self.ventana, bg="#ffffff", padx=20)
        form_frame.pack(fill="both", expand=False)

        tk.Label(form_frame, text="Buscar producto (Código o Nombre):", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#0f172a").grid(row=0, column=0, sticky="w", pady=(5,0))
        
        # Asignamos la entrada a self.ent_buscar para leerla desde la función de filtro
        self.ent_buscar = tk.Entry(form_frame, font=("Segoe UI", 10, "bold"), bd=1, relief="solid")
        self.ent_buscar.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Vincular la búsqueda en tiempo real
        self.ent_buscar.bind("<KeyRelease>", self.filtrar_inventario)

        form_frame.grid_columnconfigure(0, weight=1)

        table_frame = tk.Frame(self.ventana, bg="#2f00ff")
        table_frame.pack(fill="both", expand=True)

        columns = ("codigo", "nombre","descripcion", "precio", "cant")
        self.tabla_inv = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tabla_inv.heading("codigo", text="Código")
        self.tabla_inv.heading("nombre", text="Producto")
        self.tabla_inv.heading("descripcion",text="Descripción")
        self.tabla_inv.heading("precio", text="Precio U.")
        self.tabla_inv.heading("cant", text="Cant.")

        self.tabla_inv.column("descripcion",width=200,anchor="w")
        self.tabla_inv.column("precio", width=80, anchor="center")
        self.tabla_inv.column("cant", width=30, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla_inv.yview)
        self.tabla_inv.configure(yscroll=scrollbar.set)

        self.tabla_inv.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Cargar todos los productos inicialmente
        self.cargar_tabla_inventario(self.bd.obtener_todos_productos())

        self.tabla_inv.bind("<Button-3>", self.mostrar_menu_opciones)

    def cargar_tabla_inventario(self, productos):

        for item in self.tabla_inv.get_children():
            self.tabla_inv.delete(item)
            
        for fila in productos:
            self.tabla_inv.insert("", tk.END, values=(fila[0], fila[1], fila[2], fila[3],fila[4]))

    def filtrar_inventario(self, event=None):

        #Obtiene el texto del cuadro de búsqueda y filtra la tabla en tiempo real
        texto = self.ent_buscar.get().strip()
        
        if texto:
            productos = self.bd.buscar_productos(texto)
        else:
            productos = self.bd.obtener_todos_productos()
            
        self.cargar_tabla_inventario(productos)

    def mostrar_menu_opciones(self, event):
        # Identificar en qué fila se hizo el clic
        item_id = self.tabla_inv.identify_row(event.y)
        
        if item_id: 
            # Seleccionar visualmente la fila
            self.tabla_inv.selection_set(item_id)
            
            # Crear el menú
            menu = tk.Menu(self.ventana, tearoff=0)
            
            # Opción de edición
            menu.add_command(label="Editar producto", command=lambda: self.abrir_edicion(item_id))
            
            # Opción de eliminación
            menu.add_command(label="Eliminar producto", command=lambda: self.ejecutar_eliminacion(item_id))
            
            # Mostrar el menú en las coordenadas del ratón
            menu.tk_popup(event.x_root, event.y_root)

    def ejecutar_eliminacion(self, item_id):
        # Extraer los datos de la fila que fue seleccionada
        item_values = self.tabla_inv.item(item_id)['values']
        codigo = str(item_values[0])
        nombre = str(item_values[1])

        # Preguntar al usuario si está seguro
        respuesta = messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar el producto '{nombre}'?", parent=self.ventana)
        
        if respuesta:
            # Borrar de la Base de Datos SQLite
            self.bd.borrar_productos(codigo)
            
            # Borrar visualmente de la tabla
            self.tabla_inv.delete(item_id)
            
            messagebox.showinfo("Éxito", f"Producto '{nombre}' eliminado correctamente.", parent=self.ventana)

    def abrir_edicion(self, item_id):
        # Extraer los datos actuales de la fila
        item_values = self.tabla_inv.item(item_id)['values']
        codigo_actual = str(item_values[0])
        nombre_actual = str(item_values[1])
        descripcion_actual = str(item_values[2])
        precio_actual = str(item_values[3])
        cant_actual = str(item_values[4])

        # Crear ventana secundaria para editar
        ventana_edicion = tk.Toplevel(self.ventana)
        ventana_edicion.title("Editar Producto")
        ventana_edicion.geometry("350x250")
        ventana_edicion.configure(bg="#ffffff")
        ventana_edicion.grab_set() 

        # Variables para los Entry
        var_codigo = tk.StringVar(value=codigo_actual)
        var_nombre = tk.StringVar(value=nombre_actual)
        var_desc = tk.StringVar(value=descripcion_actual)
        var_precio = tk.StringVar(value=precio_actual)
        var_cant = tk.StringVar(value=cant_actual)

        # Formulario
        tk.Label(ventana_edicion, text="Código:", bg="#ffffff").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        tk.Entry(ventana_edicion, textvariable=var_codigo, state="readonly").grid(row=0, column=1, padx=10, pady=10)

        tk.Label(ventana_edicion, text="Nombre:", bg="#ffffff").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        tk.Entry(ventana_edicion, textvariable=var_nombre).grid(row=1, column=1, padx=10, pady=10)

        tk.Label(ventana_edicion, text="Descripción:", bg="#ffffff").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        tk.Entry(ventana_edicion, textvariable=var_desc).grid(row=2, column=1, padx=10, pady=10)

        tk.Label(ventana_edicion, text="Precio U.:", bg="#ffffff").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        tk.Entry(ventana_edicion, textvariable=var_precio).grid(row=3, column=1, padx=10, pady=10)

        tk.Label(ventana_edicion, text="Cant.:", bg="#ffffff").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        tk.Entry(ventana_edicion, textvariable=var_cant).grid(row=4, column=1, padx=10, pady=10)

        # Botón Guardar
        tk.Button(ventana_edicion, text="Guardar Cambios", 
                    command=lambda: self.guardar_edicion(
                    item_id, codigo_actual, var_nombre.get(),var_desc.get(), var_precio.get(), var_cant.get(), ventana_edicion
                    )).grid(row=5, column=0, columnspan=2, pady=15)

    def guardar_edicion(self, item_id, codigo, nuevo_nombre,nueva_desc, nuevo_precio, nueva_cant, ventana_edicion):
        # Validar que no haya campos vacíos
        if not nuevo_nombre.strip() or not str(nuevo_precio).strip() or not str(nueva_cant).strip():
            messagebox.showwarning("Atención", "Por favor, completa todos los campos antes de guardar.", parent=ventana_edicion)
            return 
        
        try:
            precio_valido = float(nuevo_precio)
            cant_valida = int(nueva_cant)
        except ValueError:
            messagebox.showwarning("Atención", "El precio debe ser un número y la cantidad un número entero.", parent=ventana_edicion)
            return 

        try:
            self.bd.actualizar_producto(codigo, nuevo_nombre, nueva_desc, precio_valido, cant_valida)
            
            # Actualizar visualmente en el Treeview
            self.tabla_inv.item(item_id, values=(codigo, nuevo_nombre, nueva_desc, precio_valido, cant_valida))
            
            messagebox.showinfo("Éxito", "Producto actualizado correctamente", parent=ventana_edicion)
            ventana_edicion.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar la base de datos: {str(e)}", parent=ventana_edicion)

    def abrir_ventana_reportes(self):
        win = tk.Toplevel(self.root)
        win.title("Reporte de Ventas y Corte de Caja")
        win.geometry("900x600")
        win.configure(bg="#ffffff")
        win.grab_set()

        top_frame = tk.Frame(win, bg="#ffffff", pady=15, padx=20)
        top_frame.pack(fill="x")

        tk.Label(top_frame, text="Fecha:", bg="#ffffff", font=("Segoe UI", 11, "bold"), fg="#334155").pack(side="left")
        
        fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d")
        ent_fecha = tk.Entry(top_frame, font=("Segoe UI", 11), bd=1, relief="solid", width=12)
        ent_fecha.insert(0, fecha_hoy)
        ent_fecha.pack(side="left", padx=(5, 15))

        # Campo para ingresar o modificar el Fondo de Caja Base
        tk.Label(top_frame, text="Fondo Inicial ($):", bg="#ffffff", font=("Segoe UI", 11, "bold"), fg="#334155").pack(side="left")
        ent_fondo = tk.Entry(top_frame, font=("Segoe UI", 11), bd=1, relief="solid", width=10)
        ent_fondo.pack(side="left", padx=(5, 10))

        table_frame = tk.Frame(win, bg="#ffffff", padx=20, pady=10)
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "codigo", "hora", "total", "pago", "cambio", "metodo")
        tabla_ventas = ttk.Treeview(table_frame, columns=columns, show="headings")
        tabla_ventas.heading("id", text="ID Venta")
        tabla_ventas.heading("codigo", text="Código")
        tabla_ventas.heading("hora", text="Fecha / Hora")
        tabla_ventas.heading("total", text="Total")
        tabla_ventas.heading("pago", text="Pago Recibido")
        tabla_ventas.heading("cambio", text="Cambio")
        tabla_ventas.heading("metodo", text="Método")

        tabla_ventas.column("id", width=80, anchor="center")
        tabla_ventas.column("codigo",width=80,anchor="center")
        tabla_ventas.column("hora", width=180, anchor="center")
        tabla_ventas.column("total", width=100, anchor="e")
        tabla_ventas.column("pago", width=100, anchor="e")
        tabla_ventas.column("cambio", width=100, anchor="e")
        tabla_ventas.column("metodo", width=90, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tabla_ventas.yview)
        tabla_ventas.configure(yscroll=scrollbar.set)
        
        tabla_ventas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        bottom_frame = tk.Frame(win, bg="#f8fafc", pady=15, padx=20)
        bottom_frame.pack(fill="x")

        lbl_fondo_caja = tk.Label(bottom_frame, text="Fondo Inicial: $0.00", font=("Segoe UI", 12), bg="#f8fafc", fg="#475569")
        lbl_fondo_caja.pack(side="left", padx=(0, 15))

        lbl_total_efectivo = tk.Label(bottom_frame, text="Efectivo en Cajón: $0.00", font=("Segoe UI", 13, "bold"), bg="#f8fafc", fg="#16a34a")
        lbl_total_efectivo.pack(side="left", padx=15)

        lbl_total_tarjeta = tk.Label(bottom_frame, text="Tarjeta: $0.00", font=("Segoe UI", 13, "bold"), bg="#f8fafc", fg="#2563eb")
        lbl_total_tarjeta.pack(side="left", padx=15)

        lbl_total_dia = tk.Label(bottom_frame, text="Total Vendido: $0.00", font=("Segoe UI", 15, "bold"), bg="#f8fafc", fg="#0f172a")
        lbl_total_dia.pack(side="right")

        tabla_ventas.bind("<Double-1>", self.ver_detalle_venta)

        def guardar_y_buscar():
            fecha = ent_fecha.get().strip()
            
            # Guardar el fondo ingresado si es válido
            texto_fondo = ent_fondo.get().strip()
            if texto_fondo:
                try:
                    monto_fondo = float(texto_fondo)
                    self.bd.guardar_fondo_caja(fecha, monto_fondo)
                except ValueError:
                    messagebox.showwarning("Atención", "El fondo inicial debe ser un número válido.", parent=win)
                    return

            # Cargar Fondo de Caja guardado
            fondo_inicial = self.bd.obtener_fondo_caja(fecha)
            ent_fondo.delete(0, tk.END)
            ent_fondo.insert(0, f"{fondo_inicial:.2f}")

            # Limpiar y rellenar tabla
            for row in tabla_ventas.get_children():
                tabla_ventas.delete(row)
                
            ventas = self.bd.obtener_ventas_por_fecha(fecha)
            for v in ventas:
                etiquetas = ('tarjeta',) if v[6] == 'Tarjeta' else ('efectivo',)
                tabla_ventas.insert("", "end", values=(v[0],v[1], v[2], f"${v[3]:.2f}", f"${v[4]:.2f}", f"${v[5]:.2f}", v[6]), tags=etiquetas)
            
            tabla_ventas.tag_configure('tarjeta', foreground="#2563eb")
            
            # Calcular Totales
            totales = self.bd.obtener_totales_por_metodo(fecha)
            ventas_efectivo = 0.0
            ventas_tarjeta = 0.0
            
            for metodo, total in totales:
                if metodo == "Efectivo" and total:
                    ventas_efectivo = total
                elif metodo == "Tarjeta" and total:
                    ventas_tarjeta = total
                    
            efectivo_total_cajon = fondo_inicial + ventas_efectivo
            gran_total_vendido = ventas_efectivo + ventas_tarjeta
            
            # Actualizar interfaz
            lbl_fondo_caja.config(text=f"Fondo Base: ${fondo_inicial:.2f}")
            lbl_total_efectivo.config(text=f"Efectivo en Cajón: ${efectivo_total_cajon:.2f}")
            lbl_total_tarjeta.config(text=f"Tarjeta: ${ventas_tarjeta:.2f}")
            lbl_total_dia.config(text=f"Total Vendido: ${gran_total_vendido:.2f}")

        btn_buscar = tk.Button(top_frame, text="🔍 Consultar / Actualizar", font=("Segoe UI", 10, "bold"),
                            bg="#3b82f6", fg="white", bd=0, padx=12, cursor="hand2", command=guardar_y_buscar)
        btn_buscar.pack(side="left", padx=10)

        # Cargar datos iniciales
        guardar_y_buscar()

        def buscar_ventas():
            # Limpiar tabla
            for row in tabla_ventas.get_children():
                tabla_ventas.delete(row)
                
            fecha = ent_fecha.get().strip()

            ventas = self.bd.obtener_ventas_por_fecha(fecha)
            for v in ventas:

                etiquetas = ('tarjeta',) if v[6] == 'Tarjeta' else ('efectivo',)
                tabla_ventas.insert("", "end", values=(v[0], v[1],v[2], f"${v[3]:.2f}", f"${v[4]:.2f}", f"${v[5]:.2f}", v[6]), tags=etiquetas)

            tabla_ventas.tag_configure('tarjeta', foreground="#2563eb")

            totales = self.bd.obtener_totales_por_metodo(fecha)
            
            total_efectivo = 0.0
            total_tarjeta = 0.0
            
            for metodo, total in totales:
                if metodo == "Efectivo" and total:
                    total_efectivo = total
                elif metodo == "Tarjeta" and total:
                    total_tarjeta = total
                    
            gran_total = total_efectivo + total_tarjeta
            
            # Actualizar los textos en pantalla
            lbl_total_efectivo.config(text=f"Efectivo en Cajón: ${total_efectivo:.2f}")
            lbl_total_tarjeta.config(text=f"En Terminal (Tarjeta): ${total_tarjeta:.2f}")
            lbl_total_dia.config(text=f"Total Vendido: ${gran_total:.2f}")

        btn_buscar = tk.Button(top_frame, text="🔍 Buscar", font=("Segoe UI", 10, "bold"),
                            bg="#3b82f6", fg="white", bd=0, padx=15, cursor="hand2", command=buscar_ventas)
        btn_buscar.pack(side="left", padx=10)

        # Autocargar ventas del día al abrir la ventana
        buscar_ventas()

    def ver_detalle_venta(self, event):
        #Obtener la tabla que donde se guardaron los detalles
        tabla = event.widget
        selected_item = tabla.selection()
        
        if not selected_item:
            return
            
        # Extraer los datos de la fila (id, fecha, total)
        item_values = tabla.item(selected_item[0])['values']
        venta_id = item_values[0]
        fecha_hora = item_values[1]
        total_str = item_values[2]
        
        # Buscar los detalles en la base de datos
        detalles = self.bd.obtener_detalle_venta(venta_id)
        
        if not detalles:
            messagebox.showinfo("Información", "No hay detalles registrados para esta venta.")
            return

        win_det = tk.Toplevel(self.root)
        win_det.title(f"Detalle de Venta #{venta_id}")
        win_det.geometry("500x450")
        win_det.configure(bg="#ffffff")
        win_det.grab_set() 

        tk.Label(win_det, text=f"🧾 TICKET DE VENTA #{venta_id}", font=("Segoe UI", 14, "bold"), bg="#ffffff", fg="#0f172a").pack(pady=(15, 5))
        tk.Label(win_det, text=f"Fecha y Hora: {fecha_hora}", font=("Segoe UI", 10), bg="#ffffff", fg="#64748b").pack(pady=(0, 15))
        
        frame_tabla = tk.Frame(win_det, bg="#ffffff", padx=20)
        frame_tabla.pack(fill="both", expand=True)
        
        cols = ("cant", "producto", "precio", "subtotal")
        tabla_det = ttk.Treeview(frame_tabla, columns=cols, show="headings", height=10)
        tabla_det.heading("cant", text="Cant.")
        tabla_det.heading("producto", text="Producto")
        tabla_det.heading("precio", text="Precio U.")
        tabla_det.heading("subtotal", text="Subtotal")
        
        tabla_det.column("cant", width=50, anchor="center")
        tabla_det.column("producto", width=220, anchor="w")
        tabla_det.column("precio", width=80, anchor="e")
        tabla_det.column("subtotal", width=90, anchor="e")
        
        scroll_det = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla_det.yview)
        tabla_det.configure(yscroll=scroll_det.set)
        
        tabla_det.pack(side="left", fill="both", expand=True)
        scroll_det.pack(side="right", fill="y")
        
        # Rellenar la tabla con los artículos
        for d in detalles:
            # d = (codigo, nombre, cantidad, precio_unitario, subtotal)
            tabla_det.insert("", "end", values=(d[2], d[1], f"${d[3]:.2f}", f"${d[4]:.2f}"))
            
        # Total en la parte inferior
        tk.Label(win_det, text=f"TOTAL COBRADO: {total_str}", font=("Segoe UI", 12, "bold"),
                bg="#ffffff", fg="#16a34a").pack(pady=15, anchor="e", padx=20)

    def dialogo_crear_apartado(self):
        if not self.carrito:
            messagebox.showwarning("Venta Vacía", "No hay productos para apartar.")
            return

        win_ap = tk.Toplevel(self.root)
        win_ap.title("Registrar Apartado")
        win_ap.geometry("350x250")
        win_ap.configure(bg="#ffffff")
        win_ap.grab_set()

        tk.Label(win_ap, text="Nuevo Apartado", font=("Segoe UI", 14, "bold"), bg="#ffffff").pack(pady=10)

        tk.Label(win_ap, text="Nombre del Cliente:", font=("Segoe UI", 10, "bold"), bg="#ffffff").pack(anchor="w", padx=20)
        ent_cliente = tk.Entry(win_ap, font=("Segoe UI", 11), bd=1, relief="solid")
        ent_cliente.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(win_ap, text="A Cuenta (Anticipo $):", font=("Segoe UI", 10, "bold"), bg="#ffffff").pack(anchor="w", padx=20)
        ent_anticipo = tk.Entry(win_ap, font=("Segoe UI", 11), bd=1, relief="solid")
        ent_anticipo.pack(fill="x", padx=20, pady=(0, 15))

        def confirmar_apartado():
            cliente = ent_cliente.get().strip()
            anticipo_str = ent_anticipo.get().strip()

            if not cliente or not anticipo_str:
                messagebox.showerror("Error", "Debes ingresar el nombre y el anticipo.", parent=win_ap)
                return

            try:
                anticipo = float(anticipo_str)
                if anticipo < 0 or anticipo > self.total_venta:
                    messagebox.showerror("Error", "El anticipo no puede ser negativo ni mayor al total.", parent=win_ap)
                    return
            except ValueError:
                messagebox.showerror("Error", "Ingresa un monto numérico válido.", parent=win_ap)
                return

            # Descontar stock
            for codigo, datos in self.carrito.items():
                self.bd.descontar_stock(codigo, datos)

            # Registro de apartados
            ap_id = self.bd.registrar_apartado(cliente, self.carrito, self.total_venta, anticipo)
            
            messagebox.showinfo("Éxito", f"Apartado #{ap_id} creado para {cliente}.\nResta: ${self.total_venta - anticipo:.2f}", parent=win_ap)
            self.limpiar_venta()
            win_ap.destroy()

        tk.Button(win_ap, text="✔ Confirmar Apartado", font=("Segoe UI", 11, "bold"), bg="#f59e0b", fg="white", 
                    bd=0, pady=8, command=confirmar_apartado).pack(fill="x", padx=20)

    def abrir_ventana_apartados(self):
        win = tk.Toplevel(self.root)
        win.title("Gestión de Apartados")
        win.state('zoomed')
        win.configure(bg="#f1f5f9")
        win.grab_set()

        tk.Label(win, text="📦 Control de Apartados", font=("Segoe UI", 18, "bold"), bg="#f1f5f9", fg="#0f172a").pack(pady=15)

        table_frame = tk.Frame(win, bg="#ffffff", padx=20, pady=10)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("id", "cliente", "fecha_ap", "fecha_liq", "total", "cuenta", "resta", "estado")
        tabla = ttk.Treeview(table_frame, columns=cols, show="headings")
        
        # Cabeceras
        tabla.heading("id", text="ID")
        tabla.heading("cliente", text="Cliente")
        tabla.heading("fecha_ap", text="Día Apartado")
        tabla.heading("fecha_liq", text="Día Liquidado")
        tabla.heading("total", text="Total")
        tabla.heading("cuenta", text="A Cuenta")
        tabla.heading("resta", text="Resta")
        tabla.heading("estado", text="Estado")

        # Tamaños
        tabla.column("id", width=50, anchor="center")
        tabla.column("cliente", width=200, anchor="w")
        tabla.column("fecha_ap", width=150, anchor="center")
        tabla.column("fecha_liq", width=150, anchor="center")
        tabla.column("total", width=80, anchor="e")
        tabla.column("cuenta", width=80, anchor="e")
        tabla.column("resta", width=80, anchor="e")
        tabla.column("estado", width=100, anchor="center")

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scroll.set)
        tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        def cargar_apartados():
            for row in tabla.get_children():
                tabla.delete(row)
            for d in self.bd.obtener_todos_apartados():
                # Colorear pendientes
                tags = ('pendiente',) if d[7] == 'Pendiente' else ('liquidado',)
                tabla.insert("", "end", values=(d[0], d[1], d[2], d[3], f"${d[4]:.2f}", f"${d[5]:.2f}", f"${d[6]:.2f}", d[7]), tags=tags)
            
            tabla.tag_configure('pendiente', foreground="#dc2626") 
            tabla.tag_configure('liquidado', foreground="#16a34a") 

        cargar_apartados()

        def abonar():
            seleccion = tabla.selection()
            if not seleccion:
                messagebox.showwarning("Atención", "Selecciona un apartado de la lista.", parent=win)
                return
            
            valores = tabla.item(seleccion[0])['values']
            ap_id = valores[0]
            cliente = valores[1]
            estado = valores[7]

            if estado == 'Liquidado':
                messagebox.showinfo("Liquidado", "Este apartado ya está pagado por completo.", parent=win)
                return

            resta = float(valores[6].replace('$', ''))

            win_abono = tk.Toplevel(win)
            win_abono.title("Abonar")
            win_abono.geometry("300x200")
            win_abono.grab_set()

            tk.Label(win_abono, text=f"Abono para: {cliente}", font=("Segoe UI", 11, "bold")).pack(pady=10)
            tk.Label(win_abono, text=f"Resta actual: ${resta:.2f}", fg="#dc2626", font=("Segoe UI", 11)).pack(pady=5)
            
            tk.Label(win_abono, text="Monto a abonar ($):").pack()
            ent_abono = tk.Entry(win_abono, font=("Segoe UI", 12))
            ent_abono.pack(pady=5)

            def procesar_abono():
                try:
                    monto = float(ent_abono.get().strip())
                    if monto <= 0 or monto > resta:
                        messagebox.showerror("Error", f"El monto debe ser entre $0.1 y ${resta:.2f}", parent=win_abono)
                        return
                    
                    nuevo_estado, nueva_resta = self.bd.abonar_a_apartado(ap_id, monto)
                    
                    if nuevo_estado == 'Liquidado':
                        messagebox.showinfo("¡Liquidado!", f"El apartado de {cliente} ha sido liquidado totalmente.", parent=win_abono)
                    else:
                        messagebox.showinfo("Éxito", f"Abono registrado. Aún resta: ${nueva_resta:.2f}", parent=win_abono)
                    
                    cargar_apartados()
                    win_abono.destroy()
                except ValueError:
                    messagebox.showerror("Error", "Ingresa un número válido.", parent=win_abono)

            tk.Button(win_abono, text="Guardar Abono", bg="#16a34a", fg="white", font=("Segoe UI", 10, "bold"), command=procesar_abono).pack(pady=10)

        # Botones de Acción abajo
        bottom_frame = tk.Frame(win, bg="#f1f5f9")
        bottom_frame.pack(pady=10)
        tk.Button(bottom_frame, text="💵 Registrar Abono / Liquidar", font=("Segoe UI", 12, "bold"),
                    bg="#3b82f6", fg="white", bd=0, padx=20, pady=10, cursor="hand2", command=abonar).pack()