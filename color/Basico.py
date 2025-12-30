import re
import tkinter as tk
from tkinter import messagebox
import time
import pyautogui
from PIL import ImageGrab
import numpy as np
from colorspacious import cspace_convert

# ======================================================
# CONFIG
# ======================================================

FILAS = 16
COLUMNAS = 16
UMBRAL = 12

PALETA_GUIA = {}

# ======================================================
# HTML → PALETA
# ======================================================

def generar_paleta(html, filas=16, columnas=16):
    hex_codes = re.findall(r'id="(#(?:[0-9A-Fa-f]{6}))"', html)
    paleta = {}

    if not hex_codes:
        raise ValueError("No se encontraron colores HEX en el HTML")

    index = 0
    for f in range(1, filas + 1):
        for c in range(1, columnas + 1):
            if index >= len(hex_codes):
                return paleta
            paleta[f"{f}-{c}"] = hex_codes[index]
            index += 1

    return paleta

# ======================================================
# COLOR LOGIC
# ======================================================

def hex_to_lab(hex_color):
    hex_color = hex_color.lstrip("#")
    rgb = [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return cspace_convert(rgb, "sRGB1", "CIELab")

def delta_e(lab1, lab2):
    return np.linalg.norm(lab1 - lab2)

def color_mas_parecido(color_hex):
    if not PALETA_GUIA:
        raise RuntimeError("Primero carga una paleta desde el HTML")

    lab_color = hex_to_lab(color_hex)
    mejor_nombre = None
    mejor_hex = None
    menor_dist = float("inf")

    for nombre, hex_base in PALETA_GUIA.items():
        lab_base = hex_to_lab(hex_base)
        dist = delta_e(lab_color, lab_base)

        if dist < menor_dist:
            menor_dist = dist
            mejor_nombre = nombre
            mejor_hex = hex_base

    if menor_dist <= UMBRAL:
        return mejor_nombre, mejor_hex, menor_dist
    else:
        return None, None, menor_dist

# ======================================================
# EYEDROPPER
# ======================================================

def tomar_pixel():
    root.withdraw()
    time.sleep(2)
    x, y = pyautogui.position()
    img = ImageGrab.grab()
    r, g, b = img.getpixel((x, y))
    root.deiconify()
    return f"#{r:02X}{g:02X}{b:02X}"

# ======================================================
# UI ACTIONS
# ======================================================

def cargar_html():
    global PALETA_GUIA

    html = html_input.get("1.0", tk.END).strip()

    if not html:
        messagebox.showwarning("Aviso", "Pega el HTML primero")
        return

    try:
        PALETA_GUIA = generar_paleta(html, FILAS, COLUMNAS)
        estado_paleta.set(f"✅ Paleta cargada ({len(PALETA_GUIA)} colores)")
    except Exception as e:
        messagebox.showerror("Error al cargar HTML", str(e))

def cuentagotas():
    try:
        hex_color = tomar_pixel()
        color_actual.set(hex_color)
        preview_actual.config(bg=hex_color)

        nombre, hex_base, dist = color_mas_parecido(hex_color)

        if nombre:
            resultado.set(
                f"Pixel: {hex_color}\n"
                f"Usar: {nombre} ({hex_base})\n"
                f"ΔE: {dist:.2f}"
            )
            preview_resultado.config(bg=hex_base)
        else:
            resultado.set(
                f"Pixel: {hex_color}\n"
                f"⚠ Fuera de guía\n"
                f"ΔE mín: {dist:.2f}"
            )
            preview_resultado.config(bg="#FFFFFF")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ======================================================
# WINDOW
# ======================================================

root = tk.Tk()
root.title("Pixel Art – Guía de Colores")
root.geometry("520x480")
root.resizable(False, False)

# ---- HTML INPUT ----
tk.Label(root, text="Pega aquí el HTML con los colores:", font=("Segoe UI", 10, "bold")).pack(pady=4)

html_input = tk.Text(root, height=8, width=64)
html_input.pack(padx=10)

tk.Button(
    root,
    text="📥 Cargar paleta desde HTML",
    command=cargar_html
).pack(pady=6)

estado_paleta = tk.StringVar(value="⏳ Paleta no cargada")
tk.Label(root, textvariable=estado_paleta).pack(pady=2)

# ---- EYEDROPPER ----
tk.Button(
    root,
    text="🎯 Tomar color del pixel",
    command=cuentagotas,
    font=("Segoe UI", 10, "bold")
).pack(pady=10)

color_actual = tk.StringVar()
resultado = tk.StringVar()

preview_actual = tk.Label(root, text="Pixel", width=24, height=2, bg="#FFFFFF")
preview_actual.pack(pady=4)

tk.Label(root, textvariable=color_actual).pack()
tk.Label(root, textvariable=resultado, justify="center").pack(pady=6)

preview_resultado = tk.Label(root, text="Guía", width=24, height=2, bg="#FFFFFF")
preview_resultado.pack(pady=4)

root.mainloop()
