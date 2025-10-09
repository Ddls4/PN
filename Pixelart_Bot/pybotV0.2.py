# PixelArt Bot - Versión 0.2 - Mejoras apartir de la versión 0.15 y 0.151
import tkinter as tk
from tkinter import simpledialog, filedialog
import json
import os
import pyautogui
from pynput import mouse, keyboard
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
        self.canvas.grid(row=3, column=0, columnspan=7, padx=10, pady=10)

        self.grid = [[0 for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.canvas.bind("<Button-1>", self.toggle_pixel)

        # --- Configuración dinámica ---
        tk.Label(root, text="Tamaño grilla:").grid(row=0, column=0, sticky="e")
        self.grid_entry = tk.Entry(root, width=5)
        self.grid_entry.insert(0, str(self.GRID_SIZE))
        self.grid_entry.grid(row=0, column=1)

        tk.Label(root, text="Tamaño celda:").grid(row=0, column=2, sticky="e")
        self.cell_entry = tk.Scale(root, from_=10, to=30, orient="horizontal", variable=self.CELL_SIZE)
        self.cell_entry.grid(row=0, column=3)

        tk.Label(root, text="Velocidad (s):").grid(row=0, column=4, sticky="e")
        self.speed_entry = tk.Scale(root, from_=0.001, to=0.1, resolution=0.001,
                                    orient="horizontal", variable=self.DRAW_SPEED)
        self.speed_entry.grid(row=0, column=5)

        # Botones principales
        tk.Button(root, text="Guardar diseño", command=self.save_template).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(root, text="Cargar diseño", command=self.load_template).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(root, text="Nuevo diseño", command=self.clear_canvas).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(root, text="Elegir puntero", command=self.set_pointer).grid(row=1, column=3, padx=5, pady=5)
        tk.Button(root, text="Generar diseño", command=self.generate_design).grid(row=1, column=4, padx=5, pady=5)
        tk.Button(root, text="Aplicar cambios", command=self.apply_settings).grid(row=1, column=5, pady=5)
        # Etiqueta de estado
        self.status_label = tk.Label(root, text="Listo.", anchor="w", fg="blue")
        self.status_label.grid(row=2, column=0, columnspan=6, sticky="we", padx=5, pady=5)

        self.pointer = None
        self.paused = False  # control de pausa

        # Listener del teclado para pausar con "p"
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()
        self.redraw()

    def set_status(self, text):
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
        if isinstance(data, list):
            self.grid = data
            self.GRID_SIZE = len(data)
        elif isinstance(data, dict):
            self.grid = data.get("grid", [])
            self.GRID_SIZE = data.get("size", len(self.grid))
        else:
            self.set_status("⚠️ Formato de archivo no válido.")
            return

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
        def delayed_draw():
            threading.Event().wait(5)
            self._draw_design()
    
        threading.Thread(target=delayed_draw, daemon=True).start()

    def _draw_design(self):
        start_x, start_y = self.pointer
        for y, row in enumerate(self.grid):
            for x, val in enumerate(row):
                if self.paused:
                    self.set_status("⏸ Pausado... esperando para continuar.")
                    while self.paused:
                        threading.Event().wait(0.1)  # Espera 100ms mientras está pausado

                if val == 1:
                    px = start_x + x * self.DRAW_CELL_SIZE
                    py = start_y + y * self.DRAW_CELL_SIZE
                    pyautogui.moveTo(px, py, duration=self.DRAW_SPEED)
                    pyautogui.click()
        self.set_status("🎨 Diseño generado exitosamente.")

    def toggle_pause(self):
        """Alternar pausa manualmente"""
        self.paused = not self.paused
        if self.paused:
            self.set_status("⏸ Pausado (tecla 'p' para continuar)")
        else:
            self.set_status("▶ Continuando...")

    def on_key_press(self, key):
        """Detectar tecla 'p' para pausar/continuar"""
        try:
            if key.char.lower() == 'p':
                self.toggle_pause()
        except AttributeError:
            pass  # otras teclas especiales se ignoran
        
if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtApp(root)
    root.mainloop()