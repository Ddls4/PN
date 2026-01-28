# paleta.py  ->  paleta[(2, 5)] = "#AABBCC"
# ======================================================
import json
import os
import re

ARCHIVO_PALETAS = "paletas.json"

class PaletteManager:

    def __init__(self):
        self.palettes = {}
        self.active_palette = None
        self.cargar_desde_json()

    # HTML EXTRACTION
    def extraer_paleta_html(self, html: str, columnas: int) -> dict:
        hexes = re.findall(r'id="(#(?:[0-9A-Fa-f]{6}))"', html)
        paleta = {}

        for i, hex_color in enumerate(hexes):
            row = i // columnas
            col = i % columnas
            key = f"{row},{col}"      
            paleta[key] = hex_color.upper()

        return paleta
    
    # -------------------------------
    # CRUD
    def guardar_paleta(self, nombre: str, paleta: dict):
        self.palettes[nombre] = paleta
        self.active_palette = nombre
        self.guardar_en_json()

    def eliminar_paleta(self, nombre: str):
        print(f"Eliminando paleta: {nombre}")

    # -------------------------------           
    # Persistencia
    def guardar_en_json(self):
        data = {
            "paletas": self.palettes,
            "activa": self.active_palette
        }
        with open(ARCHIVO_PALETAS, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def cargar_desde_json(self):
        if not os.path.exists(ARCHIVO_PALETAS):
            return

        with open(ARCHIVO_PALETAS, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.palettes = data.get("paletas", {})
        self.active_palette = data.get("activa")

    # -------------------------------
    # Paleta activa
    def set_paleta_activa(self, nombre: str):
        if nombre in self.palettes:
            self.active_palette = nombre
            self.guardar_en_json()

    def get_paleta_activa(self) -> dict | None:
        if self.active_palette:
            return self.palettes.get(self.active_palette)
        return None

    def listar_paletas(self) -> list[str]:
        return list(self.palettes.keys())

