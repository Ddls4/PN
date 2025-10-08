import tkinter as tk
from tkinter import messagebox
import threading
import pyautogui
import cv2
import numpy as np
import keyboard
import time
import math

running = False  # Control global del bot

def start_bot(r, g, b, tol, dist_min):
    global running
    running = True
    
    screen = pyautogui.screenshot()
    img_rgb = np.array(screen)
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    puntos = []

    # ⚠️ Convertir a BGR antes de generar la máscara
    color_rgb = (r, g, b)
    color_bgr = tuple(reversed(color_rgb))
    lower = np.array([max(0, c - tol) for c in color_bgr])
    upper = np.array([min(255, c + tol) for c in color_bgr])

    mask = cv2.inRange(img_bgr, lower, upper)
    coords = cv2.findNonZero(mask)
    print(f"🎯 {len(coords)} píxeles detectados.")
    if coords is None:
        print("⚠️ No se encontraron píxeles del color especificado.")
        return

    for p in coords:
        x, y = p[0]

        if not running:
            print("🛑 Bot detenido.")
            return

        if any(math.dist((x, y), q) < dist_min for q in puntos):
            continue

        pyautogui.click(x, y)
        puntos.append((x, y))
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

    # --- Usar tu método de detección ---
    color_rgb = (r, g, b)
    color_bgr = tuple(reversed(color_rgb))
    min_color = np.array([max(0, c - tol) for c in color_bgr])
    max_color = np.array([min(255, c + tol) for c in color_bgr])
    mascara = cv2.inRange(img_bgr, min_color, max_color)

    # Dibujar los puntos encontrados
    puntos = cv2.findNonZero(mascara)
    if puntos is not None:
        for p in puntos:
            x, y = p[0]
            cv2.circle(img_bgr, (x, y), 1, (0, 0, 255), -1)

    # Mostrar resultado
    cv2.imshow("Vista previa - detección precisa", img_bgr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

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

root.mainloop()
