import tkinter as tk
from ui.traductor_ui import TraductorUI

if __name__ == "__main__":
    root = tk.Tk()
    app = TraductorUI(root)
    root.mainloop()