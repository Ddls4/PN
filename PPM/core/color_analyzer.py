# color_analyzer.py     ← LAB, ΔE, similitud ← mejor color
# ======================================================
import numpy as np
from PIL import ImageGrab
import pyautogui

def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def hex_to_lab(hex_color: str) -> np.ndarray:
    rgb = np.array(hex_to_rgb(hex_color)) / 255.0
    lab = np.array([rgb])
    return lab

def color_distance(hex1: str, hex2: str) -> float:
    lab1 = hex_to_lab(hex1)
    lab2 = hex_to_lab(hex2)
    return float(np.linalg.norm(lab1 - lab2))

def recomendar_color(color_hex: str, paleta: dict) -> tuple:
    mejor = None
    menor = float("inf")

    for posicion, hex_base in paleta.items():
        d = color_distance(color_hex, hex_base)
        if d < menor:
            menor = d
            mejor = (posicion, hex_base, d)

    return mejor

def nivel_similitud(distancia: float) -> str:
    if distancia <= 0.5:
        return "Muy similar"
    elif distancia <= 1:
        return "Similar"
    elif distancia <= 2:
        return "Diferente"
    else:
        return "Muy diferente"

def capturar_pixel() -> str:
    x, y = pyautogui.position()
    img = ImageGrab.grab()
    r, g, b = img.getpixel((x, y))
    return f"#{r:02X}{g:02X}{b:02X}"
