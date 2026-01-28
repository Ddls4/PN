# cinfig_tab.py
# ======================================================
from tkinter import ttk, messagebox, scrolledtext
import tkinter as tk

from core.paleta import PaletteManager


class ConfigTab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.ctx = context
        self.crear_widgets()
        self.refrescar_paletas()


    def crear_widgets(self):
        lf = ttk.LabelFrame(self, text="HTML → Paleta")
        lf.pack(fill="x", padx=15, pady=15)

        ttk.Label(lf, text="Nombre de paleta").grid(row=0, column=0, sticky="w")
        self.nombre_var = tk.StringVar()
        ttk.Entry(lf, textvariable=self.nombre_var).grid(row=0, column=1, padx=5)

        ttk.Label(lf, text="Columnas").grid(row=1, column=0, sticky="w")
        self.cols_var = tk.IntVar(value=16)
        ttk.Entry(lf, textvariable=self.cols_var, width=6).grid(row=1, column=1, sticky="w")

        ttk.Label(lf, text="HTML").grid(row=2, column=0, sticky="nw")
        self.html_text = scrolledtext.ScrolledText(lf, width=50, height=8)
        self.html_text.grid(row=2, column=1, pady=5)

        ttk.Button(
            lf,
            text="Guardar paleta",
            command=self.guardar_paleta
        ).grid(row=3, column=1, sticky="e", pady=10)
        ttk.Button(
            lf, text="Eliminar paleta", 
            command=self.eliminar_paleta
        ).grid(row=3, column=2, pady=10)


        ttk.Label(lf, text="Paleta activa:").grid(row=5, column=0, pady=(10, 0))

        self.paleta_var = tk.StringVar()
        self.combo_paletas = ttk.Combobox(
            lf,
            textvariable=self.paleta_var,
            state="readonly",
            width=25
        )
        self.combo_paletas.grid(row=5, column=1, padx=10)
        self.combo_paletas.bind("<<ComboboxSelected>>", self.cambiar_paleta)



    def guardar_paleta(self):
        nombre = self.nombre_var.get().strip()
        html = self.html_text.get("1.0", "end")
        cols = self.cols_var.get()

        if not nombre:
            messagebox.showwarning("Error", "Nombre vacío")
            return

        paleta = self.ctx.palette_manager.extraer_paleta_html(html, cols)
        self.ctx.palette_manager.guardar_paleta(nombre, paleta)
        self.refrescar_paletas()

        messagebox.showinfo("OK", f"Paleta '{nombre}' guardada ({len(paleta)} colores)")

    def refrescar_paletas(self):
        self.ctx.palette_manager.cargar_desde_json()
        nombres = self.ctx.palette_manager.listar_paletas()
        self.combo_paletas["values"] = nombres

        activa = self.ctx.palette_manager.active_palette
        if activa:
            self.paleta_var.set(activa)

    def cambiar_paleta(self, event=None):
        nombre = self.paleta_var.get()
        self.ctx.palette_manager.set_paleta_activa(nombre)

    def eliminar_paleta(self):
        nombre = self.paleta_var.get()
        if not nombre:
            return

        if not messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar la paleta '{nombre}'?"
        ):
            return

        self.ctx.palette_manager.eliminar_paleta(nombre)
        self.refrescar_paletas()

