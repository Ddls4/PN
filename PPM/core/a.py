def capturar_area_alrededor_cursor(ancho, alto):
    x, y = pyautogui.position()
    left = max(0, x - ancho // 2)
    top = max(0, y - alto // 2)
    screen = pyautogui.screenshot(region=(left, top, ancho, alto))
    return np.array(screen), (left, top)

def start_bot(r, g, b, tol, dist_min, usar_area, area_w, area_h, orden):
    global running
    running = True

    puntos = None
    if os.path.exists("puntos_temp.npy"):
        try:
            puntos = np.load("puntos_temp.npy")
            os.remove("puntos_temp.npy")
        except Exception as e:
            print(f"⚠️ Error al cargar puntos temporales: {e}")
            puntos = None

    # Captura según configuración
    if usar_area:
        screen, offset = capturar_area_alrededor_cursor(area_w, area_h)
    else:
        screen = pyautogui.screenshot()
        offset = (0, 0)

    img_rgb = np.array(screen)
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

    if puntos is None:
        color_rgb = (r, g, b)
        color_bgr = tuple(reversed(color_rgb))
        lower = np.array([max(0, c - tol) for c in color_bgr])
        upper = np.array([min(255, c + tol) for c in color_bgr])
        mask = cv2.inRange(img_bgr, lower, upper)
        coords = cv2.findNonZero(mask)
    else:
        coords = puntos.reshape(-1, 1, 2)

    if coords is None or len(coords) == 0:
        print("⚠️ No se encontraron píxeles del color especificado.")
        return

    # 🔁 Orden de los clics
    if orden == "Izquierda → Derecha":
        coords = sorted(coords, key=lambda p: (p[0][1], p[0][0]))
    elif orden == "Arriba → Abajo":
        coords = sorted(coords, key=lambda p: (p[0][0], p[0][1]))
    elif orden == "Aleatorio":
        random.shuffle(coords)

    print(f"🎯 {len(coords)} puntos a procesar ({orden}).")

    height, width = img_bgr.shape[:2]
    usado_mask = np.zeros((height, width), dtype=bool)

    for p in coords:
        x, y = p[0]
        if y >= height or x >= width or usado_mask[y, x]:
            continue

        pyautogui.click(offset[0] + x, offset[1] + y)
        y1, y2 = max(0, y - dist_min), min(height, y + dist_min)
        x1, x2 = max(0, x - dist_min), min(width, x + dist_min)
        usado_mask[y1:y2, x1:x2] = True
        time.sleep(0.001)

        if keyboard.is_pressed("esc"):
            running = False
            print("🧨 Emergencia: tecla ESC detectada.")
            return

    print("✅ Proceso completado.")

def iniciar():
    try:
        r = int(entry_r.get())
        g = int(entry_g.get())
        b = int(entry_b.get())
        tol = int(entry_tol.get())
        dist_min = int(entry_dist.get())
        usar_area = usar_area_var.get()
        area_w = int(entry_area_w.get()) if usar_area else 0
        area_h = int(entry_area_h.get()) if usar_area else 0
        orden = orden_var.get()
    except ValueError:
        messagebox.showerror("Error", "Por favor ingresa solo números válidos.")
        return

    confirmar = messagebox.askyesno("Confirmar", "¿Seguro que quieres iniciar los clics reales?")
    if not confirmar:
        return

    hilo = threading.Thread(target=start_bot, args=(r, g, b, tol, dist_min, usar_area, area_w, area_h, orden))
    hilo.daemon = True
    hilo.start()

def detener():
    global running
    running = False
    print("🛑 Bot detenido manualmente.")

def vista_previa_y_editar(r, g, b, tol, usar_area=False, area_w=500, area_h=500, orden="Izquierda → Derecha"):
    if usar_area:
        x, y = pyautogui.position()
        left = max(0, x - area_w // 2)
        top = max(0, y - area_h // 2)
        screen = pyautogui.screenshot(region=(left, top, area_w, area_h))
        offset_x, offset_y = left, top
    else:
        screen = pyautogui.screenshot()
        offset_x, offset_y = 0, 0

    img_rgb = np.array(screen)
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

    # Crear máscara
    color_rgb = (r, g, b)
    color_bgr = tuple(reversed(color_rgb))
    lower = np.array([max(0, c - tol) for c in color_bgr])
    upper = np.array([min(255, c + tol) for c in color_bgr])
    mask = cv2.inRange(img_bgr, lower, upper)
    coords = cv2.findNonZero(mask)

    if coords is None or len(coords) == 0:
        print("⚠️ No se encontraron píxeles del color especificado.")
        return

    # Aplicar orden
    if orden == "Aleatorio":
        np.random.shuffle(coords)
    elif orden == "Arriba → Abajo":
        coords = sorted(coords, key=lambda p: (p[0][1], p[0][0]))
    else:
        coords = sorted(coords, key=lambda p: (p[0][0], p[0][1]))

    puntos_activos = set(tuple(p[0]) for p in coords)
    print(f"🎯 Vista previa: {len(puntos_activos)} puntos detectados ({orden})")

    # =======================
    # 🖱 Editor Integrado
    # =======================
    print("\n🖱 Editor integrado:")
    print("• Clic = borrar/agregar punto")
    print("• ENTER = guardar y cerrar")
    print("• ESC = salir sin guardar")
    print("• R = restaurar puntos originales")
    print("• + / - = tamaño de pincel  |  Z = reset zoom\n")

    zoom = 1.0
    brush_size = 5
    ventana = "Vista previa - Edición activa"
    img_original = img_bgr.copy()

    def actualizar_vista():
        vista = img_original.copy()
        overlay = np.zeros_like(vista, np.uint8)

        for x, y in puntos_activos:
            cv2.circle(overlay, (x, y), 2, (0, 255, 0), -1)

        vista = cv2.addWeighted(vista, 0.85, overlay, 0.5, 0)
        zoomed = cv2.resize(vista, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_NEAREST)
        cv2.imshow(ventana, zoomed)

    def click_event(event, x, y, flags, param):
        nonlocal puntos_activos
        real_x, real_y = int(x / zoom), int(y / zoom)

        if event == cv2.EVENT_LBUTTONDOWN:
            eliminados = {p for p in puntos_activos if abs(p[0] - real_x) <= brush_size and abs(p[1] - real_y) <= brush_size}
            if eliminados:
                for p in eliminados:
                    puntos_activos.remove(p)
            else:
                nuevos = [
                    (real_x + dx, real_y + dy)
                    for dx in range(-brush_size, brush_size + 1)
                    for dy in range(-brush_size, brush_size + 1)
                    if 0 <= real_x + dx < img_bgr.shape[1] and 0 <= real_y + dy < img_bgr.shape[0]
                ]
                puntos_activos.update(nuevos)
            actualizar_vista()

    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(ventana, click_event)
    actualizar_vista()

    # Bucle de edición
    while True:
        key = cv2.waitKey(30) & 0xFF
        if key == 13:  # ENTER
            cv2.destroyAllWindows()
            np.save("puntos_temp.npy", np.array([[x, y] for (x, y) in puntos_activos]))
            messagebox.showinfo("Guardado", "Puntos guardados temporalmente.")
            break
        elif key == 27:  # ESC
            cv2.destroyAllWindows()
            messagebox.showwarning("Cancelado", "Edición cancelada.")
            break
        elif key == ord('r'):
            puntos_activos = set(tuple(p[0]) for p in coords)
            actualizar_vista()
        elif key in (ord('+'), ord('=')):
            brush_size = min(50, brush_size + 2)
            print(f"🖌 Tamaño de pincel: {brush_size}")
        elif key == ord('-'):
            brush_size = max(1, brush_size - 2)
            print(f"🖌 Tamaño de pincel: {brush_size}")
        elif key == ord('z'):
            zoom = 1.0
            actualizar_vista()


def cargar_colores_guardados():
    if os.path.exists(ARCHIVO_COLORES):
        with open(ARCHIVO_COLORES, "r") as f:
            return json.load(f)
    return []

def guardar_colores(colores):
    with open(ARCHIVO_COLORES, "w") as f:
        json.dump(colores, f, indent=4)

def obtener_color_cursor():
    time.sleep(2)  # Tiempo para mover el cursor
    x, y = pyautogui.position()
    pixel = pyautogui.screenshot(region=(x, y, 1, 1)).getpixel((0, 0))
    entry_r.delete(0, tk.END); entry_r.insert(0, pixel[0])
    entry_g.delete(0, tk.END); entry_g.insert(0, pixel[1])
    entry_b.delete(0, tk.END); entry_b.insert(0, pixel[2])
    messagebox.showinfo("Color detectado", f"Color bajo cursor: {pixel}")
    return pixel

def guardar_color_actual():
    try:
        r, g, b = int(entry_r.get()), int(entry_g.get()), int(entry_b.get())
    except ValueError:
        messagebox.showerror("Error", "Color inválido.")
        return

    nombre = f"Color {r},{g},{b}"
    if any(c["rgb"] == [r, g, b] for c in colores):
        messagebox.showinfo("Duplicado", "Ese color ya está guardado.")
        return

    colores.append({"nombre": nombre, "rgb": [r, g, b]})
    guardar_colores(colores)
    actualizar_lista_colores()

def actualizar_lista_colores():
    lista_colores.delete(0, tk.END)
    for c in colores:
        nombre = c["nombre"]
        rgb = tuple(c["rgb"])
        lista_colores.insert(tk.END, f"{nombre} {rgb}")

def cargar_color_desde_lista(event):
    sel = lista_colores.curselection()
    if not sel:
        return
    index = sel[0]
    rgb = colores[index]["rgb"]
    entry_r.delete(0, tk.END); entry_r.insert(0, rgb[0])
    entry_g.delete(0, tk.END); entry_g.insert(0, rgb[1])
    entry_b.delete(0, tk.END); entry_b.insert(0, rgb[2])
