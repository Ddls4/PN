import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image
import numpy as np
from collections import Counter

contador = Counter()

class PixelColorTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.ctx = context
        self.crear_widgets()

    def crear_widgets(self):
        # Botón cargar imagen
        btn = ttk.Button(self, text="Cargar imagen", command=self.cargar_imagen)
        btn.pack(pady=5)

        # Área de salida
        self.text = tk.Text(self, height=15, width=60)
        self.text.pack(padx=5, pady=5)

    def cargar_imagen(self):
        ruta = filedialog.askopenfilename(
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.bmp"),
                ("Todos", "*.*")
            ]
        )

        if ruta:
            self.contar_pixeles(ruta)

    def contar_pixeles(self, ruta_imagen):
        self.text.delete("1.0", tk.END)
        
        # Abrir imagen
        img = Image.open(ruta_imagen).convert("RGB")
        img_array = np.array(img)
        
        for pixel in img_array.reshape(-1, 3):
            color_norm = self.normalizar_color(tuple(pixel), paso=1)
            contador[color_norm] += 1

        # Mostrar resultados (limitamos a 20)
        for rgb, cantidad in contador.most_common(20):
            hex_color = "#{:02X}{:02X}{:02X}".format(*rgb)
                
            self.text.insert(
                tk.END,
                 f"Color HEX {hex_color} - {cantidad} píxeles\n"
            )

    def normalizar_color(self, rgb, paso=1):
        return tuple((c // paso) * paso for c in rgb)

    

    



