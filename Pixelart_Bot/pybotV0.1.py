import tkinter as tk
from tkinter import simpledialog, filedialog
import json
import os
import pyautogui
import time
from pynput import mouse
import threading

GRID_SIZE = 16
CELL_SIZE = 20
DRAW_CELL_SIZE = 10  # tamaño de cada pixel al dibujar

PLANTILLAS_DIR = "plantillas"


class PixelArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PixelArt Bot")

        # Crear carpeta de plantillas si no existe
        if not os.path.exists(PLANTILLAS_DIR):
            os.makedirs(PLANTILLAS_DIR)

        # --- Lienzo de diseño ---
        self.canvas = tk.Canvas(root, width=GRID_SIZE*CELL_SIZE, height=GRID_SIZE*CELL_SIZE, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.canvas.bind("<Button-1>", self.toggle_pixel)

        # Botones
        tk.Button(root, text="Guardar diseño", command=self.save_template).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(root, text="Cargar diseño", command=self.load_template).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(root, text="Elegir puntero", command=self.set_pointer).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(root, text="Generar diseño", command=self.generate_design).grid(row=1, column=3, padx=5, pady=5)

        # Etiqueta de estado
        self.status_label = tk.Label(root, text="Listo.", anchor="w", fg="blue")
        self.status_label.grid(row=2, column=0, columnspan=4, sticky="we", padx=5, pady=5)

        self.pointer = None  # coordenada de inicio

    def set_status(self, text):
        """Actualizar la barra de estado"""
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def toggle_pixel(self, event):
        x, y = event.x // CELL_SIZE, event.y // CELL_SIZE
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            self.grid[y][x] = 1 - self.grid[y][x]
            color = "black" if self.grid[y][x] == 1 else "white"
            self.canvas.create_rectangle(
                x*CELL_SIZE, y*CELL_SIZE, (x+1)*CELL_SIZE, (y+1)*CELL_SIZE,
                fill=color, outline="gray"
            )

    def save_template(self):
        name = simpledialog.askstring("Guardar", "Nombre del diseño:")
        if not name:
            return
        filepath = os.path.join(PLANTILLAS_DIR, f"{name}.json")
        with open(filepath, "w") as f:
            json.dump(self.grid, f)
        self.set_status(f"✅ Diseño guardado en {filepath}")

    def load_template(self):
        filepath = filedialog.askopenfilename(
            title="Cargar diseño",
            initialdir=PLANTILLAS_DIR,
            filetypes=[("Archivos JSON", "*.json")]
        )
        if not filepath:
            return
        with open(filepath, "r") as f:
            self.grid = json.load(f)
        self.redraw()
        self.set_status(f"📂 Diseño cargado desde {filepath}")

    def redraw(self):
        self.canvas.delete("all")
        for y, row in enumerate(self.grid):
            for x, val in enumerate(row):
                color = "black" if val == 1 else "white"
                self.canvas.create_rectangle(
                    x*CELL_SIZE, y*CELL_SIZE, (x+1)*CELL_SIZE, (y+1)*CELL_SIZE,
                    fill=color, outline="gray"
                )

    def set_pointer(self):
        self.set_status("👉 Haz clic en el lienzo de SAI/web para establecer el puntero.")

        def run_listener():
            with mouse.Listener(on_click=lambda x, y, button, pressed: on_click(x, y, button, pressed, listener)) as listener:
                listener.join()

        def on_click(x, y, button, pressed, listener):
            if pressed:
                self.pointer = (x, y)
                self.set_status(f"📍 Puntero guardado en {self.pointer}")
                listener.stop()

        threading.Thread(target=run_listener, daemon=True).start()

    def generate_design(self):
        if not self.pointer:
            self.set_status("⚠️ Primero debes establecer el puntero.")
            return

        self.set_status("Generando en 5s... cambia a SAI/web.")
        self.root.after(5000, self._draw_design)
        
        start_x, start_y = self.pointer

        for y, row in enumerate(self.grid):
            x = 0
            while x < len(row):
                if row[x] == 1:
                    start_seg = x
                    while x < len(row) and row[x] == 1:
                        x += 1
                    end_seg = x - 1
                    pyautogui.moveTo(start_x + start_seg*DRAW_CELL_SIZE, start_y + y*DRAW_CELL_SIZE)
                    pyautogui.mouseDown()
                    pyautogui.moveTo(start_x + end_seg*DRAW_CELL_SIZE, start_y + y*DRAW_CELL_SIZE)
                    pyautogui.mouseUp()
                x += 1

        self.set_status("🎨 Diseño generado exitosamente.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtApp(root)
    root.mainloop()
    


