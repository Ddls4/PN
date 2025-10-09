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
ARCHIVO_COLORES = "colores.json"

def start_bot(r, g, b, tol, dist_min):
    global running
    running = True
    
    puntos = None
    if os.path.exists("puntos_temp.npy"):
        puntos = np.load("puntos_temp.npy")
        os.remove("puntos_temp.npy")  # Limpia el archivo temporal

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

    for p in coords:
        x, y = p[0]

        if not running:
            print("🛑 Bot detenido.")
            return

        if any(math.dist((x, y), q) < dist_min for q in puntos_usados):
            continue

        pyautogui.click(x, y)
        puntos_usados.append((x, y))
        time.sleep(0.001)

        if keyboard.is_pressed("esc"):
            running = False
            print("🧨 Emergencia: tecla ESC detectada.")
            return

    print("✅ Proceso completado.")

def vista_previa(r, g, b, tol):
    screen = pyautogui.screenshot()
    img_rgb = np.array(screen)
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

    color_rgb = (r, g, b)
    color_bgr = tuple(reversed(color_rgb))
    min_color = np.array([max(0, c - tol) for c in color_bgr])
    max_color = np.array([min(255, c + tol) for c in color_bgr])
    mascara = cv2.inRange(img_bgr, min_color, max_color)

    puntos = cv2.findNonZero(mascara)
    if puntos is not None:
        for p in puntos:
            x, y = p[0]
            cv2.circle(img_bgr, (x, y), 1, (0, 0, 255), -1)

    cv2.imshow("Vista previa - detección precisa", img_bgr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if puntos is not None:
        respuesta = messagebox.askyesno(
            "Editar puntos", "¿Deseas editar los puntos detectados antes de continuar?"
        )
        if respuesta:
            puntos_editados = editar_puntos(img_bgr, puntos)
            if puntos_editados is not None:
                np.save("puntos_temp.npy", puntos_editados)
                messagebox.showinfo("Guardado", "Puntos editados guardados temporalmente.")
            else:
                messagebox.showwarning("Cancelado", "Edición cancelada.")

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

def editar_puntos(img, puntos):
    print("🖱 Fase de edición: clic para quitar/agregar puntos. ENTER = continuar, ESC = cancelar.")
    puntos_activos = set(tuple(p[0]) for p in puntos)
    
    def actualizar_vista():
        temp = img.copy()
        for x, y in puntos_activos:
            cv2.circle(temp, (x, y), 2, (0, 0, 255), -1)
        cv2.imshow("Editor de puntos", temp)

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            punto = (x, y)
            cercano = min(
                puntos_activos,
                key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2,
                default=None
            )
            if cercano and abs(cercano[0] - x) < 3 and abs(cercano[1] - y) < 3:
                puntos_activos.remove(cercano)
                print(f"❌ Quitado punto {cercano}")
            else:
                puntos_activos.add(punto)
                print(f"➕ Agregado punto {punto}")
            actualizar_vista()

    cv2.namedWindow("Editor de puntos")
    cv2.setMouseCallback("Editor de puntos", click_event)
    actualizar_vista()

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # ENTER = aceptar
            cv2.destroyAllWindows()
            return np.array([[x, y] for (x, y) in puntos_activos])
        elif key == 27:  # ESC = cancelar
            cv2.destroyAllWindows()
            return None

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


# GUI
root = tk.Tk()
root.title("AutoPixelBot")
root.geometry("300x320")

tk.Label(root, text="🎨 AutoPixelBot", font=("Arial", 14, "bold")).pack(pady=5)
tk.Label(root, text="Color objetivo (RGB)").pack()
frame_rgb = tk.Frame(root)
frame_rgb.pack()
entry_r = tk.Entry(frame_rgb, width=5); entry_r.insert(0, "0"); entry_r.pack(side="left")
entry_g = tk.Entry(frame_rgb, width=5); entry_g.insert(0, "0"); entry_g.pack(side="left")
entry_b = tk.Entry(frame_rgb, width=5); entry_b.insert(0, "0"); entry_b.pack(side="left")

tk.Label(root, text="Tolerancia:").pack()
entry_tol = tk.Entry(root, width=10)
entry_tol.insert(0, "10")
entry_tol.pack()

tk.Label(root, text="Distancia mínima (px):").pack()
entry_dist = tk.Entry(root, width=10)
entry_dist.insert(0, "10")
entry_dist.pack()

tk.Button(root, text="Vista previa", command=lambda: vista_previa(
    int(entry_r.get()), int(entry_g.get()), int(entry_b.get()), int(entry_tol.get()))
).pack(pady=5)

tk.Button(root, text="Iniciar", bg="lightgreen", command=iniciar).pack(pady=5)
tk.Button(root, text="🛑 Parar", bg="red", command=detener).pack(pady=5)

tk.Label(root, text="(Pulsa ESC para detener en emergencia)", fg="gray").pack(pady=10)


# Cargar colores desde JSON
colores = cargar_colores_guardados()

# Panel lateral de colores
frame_colores = tk.Frame(root, bd=2, relief="groove")
frame_colores.place(x=320, y=10, width=250, height=300)

tk.Label(frame_colores, text="🎨 Colores guardados", font=("Arial", 10, "bold")).pack(pady=5)
tk.Button(frame_colores, text="Obtener color bajo cursor", command=obtener_color_cursor).pack(pady=3)
tk.Button(frame_colores, text="Guardar color actual", command=guardar_color_actual).pack(pady=3)

lista_colores = tk.Listbox(frame_colores, height=10)
lista_colores.pack(pady=5, fill="both", expand=True)
lista_colores.bind("<<ListboxSelect>>", cargar_color_desde_lista)

actualizar_lista_colores()


root.mainloop()
