import tkinter as tk
from tkinter import simpledialog, filedialog
import json
import os
import pyautogui
from pynput import mouse
import threading

PLANTILLAS_DIR = "plantillas"


class PixelArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PixelArt Bot")

        # Valores configurables (default)
        self.GRID_SIZE = 32
        self.CELL_SIZE = 20
        self.DRAW_CELL_SIZE = 10
        self.DRAW_SPEED = 0.01

        # Crear carpeta de plantillas si no existe
        if not os.path.exists(PLANTILLAS_DIR):
            os.makedirs(PLANTILLAS_DIR)

        # --- Lienzo de diseño ---
        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=6, padx=10, pady=10)

        self.grid = [[0 for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.canvas.bind("<Button-1>", self.toggle_pixel)

        # Botones principales
        tk.Button(root, text="Guardar diseño", command=self.save_template).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(root, text="Cargar diseño", command=self.load_template).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(root, text="Nuevo diseño", command=self.clear_canvas).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(root, text="Elegir puntero", command=self.set_pointer).grid(row=1, column=3, padx=5, pady=5)
        tk.Button(root, text="Generar diseño", command=self.generate_design).grid(row=1, column=4, padx=5, pady=5)

        # --- Configuración dinámica ---
        tk.Label(root, text="Grid:").grid(row=2, column=0, sticky="e")
        self.grid_entry = tk.Entry(root, width=5)
        self.grid_entry.insert(0, str(self.GRID_SIZE))
        self.grid_entry.grid(row=2, column=1)

        tk.Label(root, text="Cell:").grid(row=2, column=2, sticky="e")
        self.cell_entry = tk.Entry(root, width=5)
        self.cell_entry.insert(0, str(self.CELL_SIZE))
        self.cell_entry.grid(row=2, column=3)

        tk.Label(root, text="Velocidad:").grid(row=2, column=4, sticky="e")
        self.speed_entry = tk.Entry(root, width=5)
        self.speed_entry.insert(0, str(self.DRAW_SPEED))
        self.speed_entry.grid(row=2, column=5)

        tk.Button(root, text="Aplicar cambios", command=self.apply_settings).grid(row=3, column=0, columnspan=6, pady=5)

        # Etiqueta de estado
        self.status_label = tk.Label(root, text="Listo.", anchor="w", fg="blue")
        self.status_label.grid(row=4, column=0, columnspan=6, sticky="we", padx=5, pady=5)

        self.pointer = None
        self.redraw()

    def set_status(self, text):
        """Actualizar la barra de estado"""
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def apply_settings(self):
        """Actualizar GRID_SIZE, CELL_SIZE y DRAW_SPEED desde la interfaz"""
        try:
            new_grid = int(self.grid_entry.get())
            new_cell = int(self.cell_entry.get())
            new_speed = float(self.speed_entry.get())
        except ValueError:
            self.set_status("⚠️ Valores inválidos en configuración.")
            return

        self.GRID_SIZE = new_grid
        self.CELL_SIZE = new_cell
        self.DRAW_SPEED = new_speed
        self.grid = [[0 for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.redraw()
        self.set_status(f"🔧 Configuración aplicada: Grid {self.GRID_SIZE}, Cell {self.CELL_SIZE}, Vel {self.DRAW_SPEED}")

    def toggle_pixel(self, event):
        x, y = event.x // self.CELL_SIZE, event.y // self.CELL_SIZE
        if 0 <= x < len(self.grid) and 0 <= y < len(self.grid):
            self.grid[y][x] = 1 - self.grid[y][x]
            color = "black" if self.grid[y][x] == 1 else "white"
            self.canvas.create_rectangle(
                x*self.CELL_SIZE, y*self.CELL_SIZE,
                (x+1)*self.CELL_SIZE, (y+1)*self.CELL_SIZE,
                fill=color, outline="gray"
            )

    def save_template(self):
        name = simpledialog.askstring("Guardar", "Nombre del diseño:")
        if not name:
            return
        filepath = os.path.join(PLANTILLAS_DIR, f"{name}.json")
        data = {"size": self.GRID_SIZE, "grid": self.grid}
        with open(filepath, "w") as f:
            json.dump(data, f)
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
            data = json.load(f)
        self.GRID_SIZE = data.get("size", 16)
        self.grid = data.get("grid", [])
        self.grid_entry.delete(0, tk.END)
        self.grid_entry.insert(0, str(self.GRID_SIZE))
        self.redraw()
        self.set_status(f"📂 Diseño cargado desde {filepath}")

    def redraw(self):
        """Redibujar el lienzo"""
        self.canvas.config(width=self.GRID_SIZE*self.CELL_SIZE, height=self.GRID_SIZE*self.CELL_SIZE)
        self.canvas.delete("all")
        for y, row in enumerate(self.grid):
            for x, val in enumerate(row):
                color = "black" if val == 1 else "white"
                self.canvas.create_rectangle(
                    x*self.CELL_SIZE, y*self.CELL_SIZE,
                    (x+1)*self.CELL_SIZE, (y+1)*self.CELL_SIZE,
                    fill=color, outline="gray"
                )

    def clear_canvas(self):
        self.grid = [[0 for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.redraw()
        self.set_status("🗑️ Lienzo limpiado.")

    def set_pointer(self):
        self.set_status("👉 Haz clic en el lienzo de SAI/web para establecer el puntero.")

        def run_listener():
            def on_click(x, y, button, pressed):
                if pressed:
                    self.pointer = (x, y)
                    self.set_status(f"📍 Puntero guardado en {self.pointer}")
                    listener.stop()

            with mouse.Listener(on_click=on_click) as listener:
                listener.join()

        threading.Thread(target=run_listener, daemon=True).start()

    def generate_design(self):
        if not self.pointer:
            self.set_status("⚠️ Primero debes establecer el puntero.")
            return

        self.set_status("Generando en 5s... cambia a SAI/web.")
        self.root.after(5000, self._draw_design)

    def _draw_design(self):
        start_x, start_y = self.pointer
        for y, row in enumerate(self.grid):
            x = 0
            while x < len(row):
                if row[x] == 1:
                    start_seg = x
                    while x < len(row) and row[x] == 1:
                        x += 1
                    end_seg = x - 1
                    pyautogui.moveTo(start_x + start_seg*self.DRAW_CELL_SIZE,
                                     start_y + y*self.DRAW_CELL_SIZE,
                                     duration=self.DRAW_SPEED)
                    pyautogui.mouseDown()
                    pyautogui.moveTo(start_x + end_seg*self.DRAW_CELL_SIZE,
                                     start_y + y*self.DRAW_CELL_SIZE,
                                     duration=self.DRAW_SPEED)
                    pyautogui.mouseUp()
                x += 1
        self.set_status("🎨 Diseño generado exitosamente.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtApp(root)
    root.mainloop()
