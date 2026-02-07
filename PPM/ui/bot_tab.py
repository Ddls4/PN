# bot_tab.py
from tkinter import ttk, messagebox
import threading

from core.bot import start_bot, stop_bot, vista_previa_y_editar_hex


class Bottab(ttk.Frame):
    def __init__(self, parent, context):
        super().__init__(parent)
        self.ctx = context
        self.crear_widgets()

    def crear_widgets(self):
        ttk.Label(self, text="🤖 Pintado Automático (BOT)").grid(
            row=0, column=0, columnspan=2, pady=10
        )

        # =========================
        # Color HEX
        # =========================
        ttk.Label(self, text="Color HEX (#RRGGBB)").grid(
            row=1, column=0, sticky="w"
        )
        self.entry_hex = ttk.Entry(self)
        self.entry_hex.insert(0, "#FFFFFF")
        self.entry_hex.grid(row=1, column=1, padx=10, pady=5)

        # =========================
        # Tolerancia
        # =========================
        ttk.Label(
            self,
            text="Tolerancia (detección de color)"
        ).grid(row=2, column=0, sticky="w")

        self.entry_tol = ttk.Entry(self)
        self.entry_tol.insert(0, "1")
        self.entry_tol.grid(row=2, column=1, padx=10, pady=5)

        # =========================
        # Orden
        # =========================
        ttk.Label(self, text="Orden de clics").grid(
            row=3, column=0, sticky="w"
        )
        self.combo_orden = ttk.Combobox(
            self,
            values=[
                "Izquierda → Derecha",
                "Arriba → Abajo",
                "Aleatorio"
            ],
            state="readonly"
        )
        self.combo_orden.current(0)
        self.combo_orden.grid(row=3, column=1, padx=10, pady=5)

        # =========================
        # Botones
        # =========================
        ttk.Button(
            self,
            text="▶ Iniciar",
            command=self.iniciar
        ).grid(row=4, column=0, pady=15)

        ttk.Button(
            self,
            text="⛔ Detener",
            command=stop_bot
        ).grid(row=4, column=1, pady=15)

        ttk.Button(
            self,
            text="👁 Vista previa / Editor",
            command=self.vista_previa
        ).grid(row=5, column=0, columnspan=2, pady=10)

    # =========================
    # Acciones
    # =========================
    def iniciar(self):
        try:
            hex_color = self.entry_hex.get().strip()
            tol = int(self.entry_tol.get())
            orden = self.combo_orden.get()

            if not hex_color.startswith("#") or len(hex_color) != 7:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Error",
                "Color HEX inválido o valores incorrectos."
            )
            return

        if not messagebox.askyesno(
            "Confirmar",
            "⚠️ El bot hará clics reales.\n¿Deseas continuar?"
        ):
            return

        hilo = threading.Thread(
            target=start_bot,
            args=(hex_color, tol, orden),
            daemon=True
        )
        hilo.start()

    def vista_previa(self):
        try:
            hex_color = self.entry_hex.get().strip()
            tol = int(self.entry_tol.get())
            orden = self.combo_orden.get()

            if not hex_color.startswith("#") or len(hex_color) != 7:
                raise ValueError

        except ValueError:
            messagebox.showerror("Error", "Valores inválidos")
            return

        # 🔹 Vista previa en hilo para no congelar la UI
        hilo = threading.Thread(
            target=vista_previa_y_editar_hex,
            kwargs=dict(
                hex_color=hex_color,
                tol=tol,
                orden=orden
            ),
            daemon=True
        )
        hilo.start()
