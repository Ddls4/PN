import tkinter as tk
from tkinter import simpledialog, filedialog
import json
import os
import pyautogui
import time
from pynput import mouse, keyboard
import threading

PLANTILLAS_DIR = "plantillas"


class PixelArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PixelArt Bot")
        self.root.minsize(500, 400)
        self.root.maxsize(1920, 1080)

        # Carpeta de plantillas
        if not os.path.exists(PLANTILLAS_DIR):
            os.makedirs(PLANTILLAS_DIR)

        # Variables configurables
        self.GRID_SIZE = tk.IntVar(value=32)
        self.CELL_SIZE = tk.IntVar(value=20)
        self.DRAW_SPEED = tk.DoubleVar(value=0.01)
        # --- Controles superiores ---
        top_frame = tk.Frame(root)
        top_frame.grid(row=0, column=0, sticky="we", pady=5)



        # --- Controles con sliders ---
        controls_frame = tk.Frame(top_frame)
        controls_frame.grid(row=0, column=0, padx=10)

        tk.Label(controls_frame, text="Tamaño grilla").grid(row=0, column=0)
        self.grid_slider = tk.Scale(controls_frame, from_=8, to=100, orient="horizontal", variable=self.GRID_SIZE)
        self.grid_slider.grid(row=0, column=1)

        tk.Label(controls_frame, text="Tamaño celda").grid(row=1, column=0)
        self.cell_slider = tk.Scale(controls_frame, from_=5, to=30, orient="horizontal", variable=self.CELL_SIZE)
        self.cell_slider.grid(row=1, column=1)

        tk.Label(controls_frame, text="Velocidad (s)").grid(row=2, column=0)
        self.speed_slider = tk.Scale(controls_frame, from_=0.001, to=0.1, resolution=0.001,
                                    orient="horizontal", variable=self.DRAW_SPEED)
        self.speed_slider.grid(row=2, column=1)

        tk.Button(controls_frame, text="Aplicar cambios", command=self.apply_changes).grid(row=3, column=0, columnspan=2, pady=5)

        # --- Botones de acción ---
        buttons_frame = tk.Frame(top_frame)
        buttons_frame.grid(row=0, column=1, padx=10)

        tk.Button(buttons_frame, text="Guardar diseño", command=self.save_template).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(buttons_frame, text="Cargar diseño", command=self.load_template).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(buttons_frame, text="Elegir puntero", command=self.set_pointer).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(buttons_frame, text="Generar diseño", command=self.generate_design).grid(row=1, column=1, padx=5, pady=5)

        # --- Lienzo ---
        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.grid(row=1, column=0, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.toggle_pixel)

        # --- Estado ---
        self.status_label = tk.Label(root, text="Listo.", anchor="w", fg="blue")
        self.status_label.grid(row=2, column=0, sticky="we", padx=5, pady=5)

        self.pointer = None
        self.paused = False  # control de pausa

        # Listener del teclado para pausar con "p"
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

        self.reset_grid()

    def set_status(self, text):
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def reset_grid(self):
        size = self.GRID_SIZE.get()
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        for y, row in enumerate(self.grid):
            for x, val in enumerate(row):
                color = "black" if val == 1 else "white"
                self.canvas.create_rectangle(
                    x*self.CELL_SIZE.get(), y*self.CELL_SIZE.get(),
                    (x+1)*self.CELL_SIZE.get(), (y+1)*self.CELL_SIZE.get(),
                    fill=color, outline="gray"
                )

    def toggle_pixel(self, event):
        x, y = event.x // self.CELL_SIZE.get(), event.y // self.CELL_SIZE.get()
        if 0 <= x < self.GRID_SIZE.get() and 0 <= y < self.GRID_SIZE.get():
            self.grid[y][x] = 1 - self.grid[y][x]
            self.redraw()

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
        self.GRID_SIZE.set(len(self.grid))
        self.redraw()
        self.set_status(f"📂 Diseño cargado desde {filepath}")

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

    def apply_changes(self):
        # Actualizar los IntVar en vez de sobrescribirlos
        self.GRID_SIZE.set(self.grid_slider.get())
        self.CELL_SIZE.set(self.cell_slider.get())
        self.DRAW_SPEED.set(self.speed_slider.get())  # ya está en segundos, no dividas por 1000

        # Rehacer la grilla con los nuevos valores
        size = self.GRID_SIZE.get()
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.canvas.config(width=size * self.CELL_SIZE.get(),
                        height=size * self.CELL_SIZE.get())

        # Ajustar ventana automáticamente al nuevo canvas
        self.root.update_idletasks()
        self.root.geometry("")  # <-- se adapta al contenido

        self.redraw()
        self.set_status("🔄 Cambios aplicados en la grilla y celdas.")

    def generate_design(self):
        if not self.pointer:
            self.set_status("⚠️ Primero debes establecer el puntero.")
            return

        def run():
            self.set_status("Generando en 5s... cambia a SAI/web.")
            time.sleep(5)

            start_x, start_y = self.pointer
            draw_size = 10  # tamaño fijo del "pixel real"

            for y, row in enumerate(self.grid):
                x = 0
                while x < len(row):
                    if row[x] == 1:
                        start_seg = x
                        while x < len(row) and row[x] == 1:
                            x += 1
                        end_seg = x - 1

                        pyautogui.moveTo(start_x + start_seg*draw_size, start_y + y*draw_size)
                        pyautogui.mouseDown()
                        pyautogui.moveTo(start_x + end_seg*draw_size, start_y + y*draw_size)
                        pyautogui.mouseUp()

                        # velocidad y pausa
                        for _ in range(int(self.DRAW_SPEED.get() * 100)):
                            while self.paused:
                                time.sleep(0.1)
                            time.sleep(0.01)
                    x += 1
            self.set_status("🎨 Diseño generado exitosamente.")

        threading.Thread(target=run, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtApp(root)
    root.mainloop()
