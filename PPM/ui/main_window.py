import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from ui.config_tab import ConfigTab
from ui.color_rec_tab import ColorRecTab
from ui.bot_tab import Bottab

from core.paleta import PaletteManager

class AppContext:
    def __init__(self):
        self.palette_manager = PaletteManager()

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PPM - Pixel Palette Matcher")
        self.geometry("620x520") # 900x600

        self.context = AppContext()
        self.crear_tabs()

    def crear_tabs(self):
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        notebook.add(
            ConfigTab(notebook, self.context),
            text="Configuración / Paletas"
        )

        notebook.add(
            ColorRecTab(notebook, self.context),
            text="Recomendar Colores"
        )

        notebook.add(
            Bottab(notebook, self.context),
            text="Bot "
        )

