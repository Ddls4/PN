# color_rec_tab.py
# ======================================================
from tkinter import ttk, messagebox
from core.color_analyzer import recomendar_color, capturar_pixel, nivel_similitud
import tkinter as tk
import keyboard
import threading


class ColorRecTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.ctx = context
        self.crear_widgets()

    def crear_widgets(self):
        lf = ttk.LabelFrame(self, text="Recomendación de color")
        lf.pack(fill="both", expand=True, padx=15, pady=15)

        self.color_actual = tk.StringVar(value="—")
        self.resultado = tk.StringVar(value="Esperando...")

        ttk.Label(lf, text="Color detectado").grid(row=0, column=0, sticky="w")
        ttk.Label(lf, textvariable=self.color_actual).grid(row=0, column=1, sticky="w")

        ttk.Button(
            lf,
            text="Modo captura (F1)",
            command=self.activar_modo_captura
        ).grid(row=1, column=0, pady=10)

        ttk.Label(lf, textvariable=self.resultado, justify="left").grid(
            row=2, column=0, columnspan=2, pady=10
        )

        self.preview = tk.Label(lf, width=20, height=2, bg="#FFFFFF")
        self.preview.grid(row=3, column=0, columnspan=2, pady=5)

    def activar_modo_captura(self):
        self.resultado.set("🎯 Modo captura activo\nPresione F1")
        threading.Thread(target=self._esperar_f1, daemon=True).start()

    def _esperar_f1(self):
        keyboard.wait("F1")

        hex_color = capturar_pixel()

        self.after(0, lambda: self._procesar_color(hex_color))

    def _procesar_color(self, hex_color):
        paleta = self.ctx.palette_manager.get_paleta_activa()
        if not paleta:
            messagebox.showwarning("Error", "No hay paleta activa")
            return

        self.color_actual.set(hex_color)

        pos, hex_base, dist = recomendar_color(hex_color, paleta)
        nivel = nivel_similitud(dist)

        self.resultado.set(
            f"Pixel: {hex_color}\n"
            f"Usar: {hex_base}\n"
            f"ΔE: {dist:.2f} ({nivel})"
        )

        self.preview.config(bg=hex_base)


