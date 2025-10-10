import tkinter as tk
from tkinter import messagebox
import threading
import pyautogui
import cv2
import numpy as np
import keyboard
import time
import math
import json
import os

running = False  # Control global del bot
ARCHIVO_COLORES = "colores.json" # colores_guardados


def start_bot(r, g, b, tol, dist_min):
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

    if puntos is None:
        screen = pyautogui.screenshot()
        img_rgb = np.array(screen)
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

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

    print(f"🎯 {len(coords)} puntos a procesar.")
    puntos_usados = []

    usado_mask = np.zeros(mask.shape, dtype=bool)
    for p in coords:
        x, y = p[0]
        if usado_mask[y, x]:  # ya visitado
            continue

        pyautogui.click(x, y)
        usado_mask[y-dist_min:y+dist_min, x-dist_min:x+dist_min] = True
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
    except ValueError:
        messagebox.showerror("Error", "Por favor ingresa solo números válidos.")
        return
   

    confirmar = messagebox.askyesno("Confirmar", "¿Seguro que quieres iniciar los clics reales?")
    if not confirmar:
        return

    hilo = threading.Thread(target=start_bot, args=(r, g, b, tol, dist_min))
    hilo.daemon = True
    hilo.start()

def detener():
    global running
    running = False
    print("🛑 Bot detenido manualmente.")

def vista_previa_y_editar(r, g, b, tol):
    screen = pyautogui.screenshot()
    img_rgb = np.array(screen)
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

    color_rgb = (r, g, b)
    color_bgr = tuple(reversed(color_rgb))
    min_color = np.array([max(0, c - tol) for c in color_bgr])
    max_color = np.array([min(255, c + tol) for c in color_bgr])
    mascara = cv2.inRange(img_bgr, min_color, max_color)
    puntos = cv2.findNonZero(mascara)
    puntos_activos = set(tuple(p[0]) for p in puntos) if puntos is not None else set()

    print("🖱 Editor integrado: clic = borrar/agregar | ENTER = guardar | ESC = salir | R = restaurar")
    print("Usa + / - para zoom ")
    print("Usa [ / ] para cambiar tamaño de pincel")

    zoom = 1.0
    brush_size = 5
    ventana = "Vista previa - edición activa"
    img_original = img_bgr.copy()

    def actualizar_vista():
        vista = img_original.copy()
        overlay = np.zeros_like(vista, np.uint8)

        # Dibujar puntos activos como verde brillante (no confunde con rojos)
        for x, y in puntos_activos:
            cv2.circle(overlay, (x, y), 2, (0, 255, 0), -1)

        # Combinar imagen original con overlay
        vista = cv2.addWeighted(vista, 0.85, overlay, 0.5, 0)
        zoomed = cv2.resize(vista, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_NEAREST)
        cv2.imshow(ventana, zoomed)

    def click_event(event, x, y, flags, param):
        nonlocal puntos_activos
        real_x, real_y = int(x / zoom), int(y / zoom)
        if event == cv2.EVENT_LBUTTONDOWN:
            eliminados = {p for p in puntos_activos if abs(p[0] - real_x) <= brush_size and abs(p[1] - real_y) <= brush_size}
            if eliminados:
                for p in eliminados: puntos_activos.remove(p)
            else:
                nuevos = [(real_x + dx, real_y + dy)
                          for dx in range(-brush_size, brush_size + 1)
                          for dy in range(-brush_size, brush_size + 1)
                          if 0 <= real_x + dx < img_bgr.shape[1] and 0 <= real_y + dy < img_bgr.shape[0]]
                puntos_activos.update(nuevos)
            actualizar_vista()

    cv2.namedWindow(ventana, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(ventana, click_event)
    actualizar_vista()

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
            puntos_activos = set(tuple(p[0]) for p in puntos)
            actualizar_vista()
        elif key == ord('+') or key == ord('='):
            zoom = min(5.0, zoom + 0.2)
            actualizar_vista()
        elif key == ord('-') and zoom > 0.4:
            zoom = max(0.4, zoom - 0.2)
            actualizar_vista()
        elif key == ord(']'):
            brush_size = min(50, brush_size + 2)
            print(f"🖌 Tamaño de pincel: {brush_size}")
        elif key == ord('['):
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

colores = cargar_colores_guardados()
# GUI
# --- Ventana principal ---
root = tk.Tk()
root.title("🎨 AutoPixelBot")
root.geometry("600x360")
root.resizable(False, False)

# --- Panel Izquierdo: Configuración ---
frame_left = tk.Frame(root, padx=10, pady=10)
frame_left.pack(side="left", fill="y")

tk.Label(frame_left, text="AutoPixelBot", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 10))

# Entradas RGB
tk.Label(frame_left, text="Color objetivo (RGB):").grid(row=1, column=0, columnspan=3, sticky="w")
entry_r = tk.Entry(frame_left, width=5); entry_r.insert(0, "0"); entry_r.grid(row=2, column=0)
entry_g = tk.Entry(frame_left, width=5); entry_g.insert(0, "0"); entry_g.grid(row=2, column=1)
entry_b = tk.Entry(frame_left, width=5); entry_b.insert(0, "0"); entry_b.grid(row=2, column=2)

# Tolerancia
tk.Label(frame_left, text="Tolerancia:").grid(row=3, column=0, columnspan=3, sticky="w", pady=(10, 0))
entry_tol = tk.Entry(frame_left, width=10)
entry_tol.insert(0, "10")
entry_tol.grid(row=4, column=0, columnspan=3)

# Distancia mínima
tk.Label(frame_left, text="Distancia mínima (px):").grid(row=5, column=0, columnspan=3, sticky="w", pady=(10, 0))
entry_dist = tk.Entry(frame_left, width=10)
entry_dist.insert(0, "10")
entry_dist.grid(row=6, column=0, columnspan=3)

# Botones principales
tk.Button(frame_left, text="🖼 Vista previa", width=18,
          command=lambda: vista_previa_y_editar(
              int(entry_r.get()), int(entry_g.get()), int(entry_b.get()), int(entry_tol.get()))
          ).grid(row=7, column=0, columnspan=3, pady=(15, 3))

tk.Button(frame_left, text="▶ Iniciar", bg="lightgreen", width=18, command=iniciar).grid(row=8, column=0, columnspan=3, pady=3)
tk.Button(frame_left, text="🛑 Parar", bg="red", fg="white", width=18, command=detener).grid(row=9, column=0, columnspan=3, pady=3)

tk.Label(frame_left, text="Pulsa ESC para detener en emergencia", fg="gray", font=("Arial", 8)).grid(row=10, column=0, columnspan=3, pady=(10, 0))

# --- Panel Derecho: Colores guardados ---
frame_right = tk.Frame(root, bd=2, relief="groove", padx=10, pady=10)
frame_right.pack(side="right", fill="both", expand=True)

tk.Label(frame_right, text="🎨 Colores guardados", font=("Arial", 12, "bold")).pack(pady=(0, 10))

btn_color_cursor = tk.Button(frame_right, text="🎯 Obtener color bajo cursor", command=obtener_color_cursor)
btn_color_cursor.pack(fill="x", pady=2)

btn_guardar_color = tk.Button(frame_right, text="💾 Guardar color actual", command=guardar_color_actual)
btn_guardar_color.pack(fill="x", pady=2)

lista_colores = tk.Listbox(frame_right, height=12)
lista_colores.pack(fill="both", expand=True, pady=8)
lista_colores.bind("<<ListboxSelect>>", cargar_color_desde_lista)

# Si tienes más funciones, como editar o eliminar color, podrías agregar botones aquí:
frame_botones_colores = tk.Frame(frame_right)
frame_botones_colores.pack(fill="x")
tk.Button(frame_botones_colores, text="✏️ Editar puntos", command=lambda: print("Editar puntos (futuro)")).pack(side="left", expand=True, fill="x", padx=2)
tk.Button(frame_botones_colores, text="🗑 Eliminar color", command=lambda: print("Eliminar color (futuro)")).pack(side="left", expand=True, fill="x", padx=2)

# Actualizar la lista inicial
actualizar_lista_colores()

root.mainloop()