# menu.py
import tkinter as tk
from tkinter import *

import customtkinter as ctk


from views.TTSm1 import TTSm1_frame
from views.TTSm2 import TTSm2_frame
from views.TTScv import create_frame_one
from funciones import tesseract_pach


def create_main_window():
    ctk.set_appearance_mode("light") # system dark light
    ctk.set_default_color_theme("dark-blue")
    root = tk.Tk()
    root.title("TTS_Ddls4")
    root.geometry("500x480")
    return root

def create_menu():
    root = create_main_window()
    # Crear marco contenedor
    container = tk.Frame(root)
    container.pack(fill="both", expand=True)
    # Crear marcos individuales
    TTS_m1_frame = TTSm1_frame(container)
    TTS_m2_frame = TTSm2_frame(container)
    TTS_cv_frame = create_frame_one(container)
    # Función para cambiar de marco
    def show_frame(frame,tamaño):
        frame.tkraise()
        root.geometry(tamaño)

    # Colocar botones de navegación en la ventana principal
    button_frame = tk.Frame(root) # bg="red"
    button_frame.pack(side="top", fill="x")

    ctk.CTkButton(button_frame, text="Modo 1", command=lambda: show_frame(TTS_m1_frame,"500x480"),width=50).pack(side="left", padx=5, pady=5)
    ctk.CTkButton(button_frame, text="Modo 2", command=lambda: show_frame(TTS_m2_frame,"1200x400"),width=50).pack(side="left", padx=5, pady=5) # 1200x400 y 800x400
    ctk.CTkButton(button_frame, text="Modo 3", command=lambda: show_frame(TTS_cv_frame,"850x350"),width=50).pack(side="left", padx=5, pady=5)
    # Mostrar el primer frame por defecto
    

    txtt = ctk.CTkLabel(button_frame, text="Root")
    txtt.pack(side="right", padx=5, pady=5)
    ctk.CTkButton(button_frame,text="Elegir", command=lambda: tesseract_pach(txtt),width=50).pack(side="right", padx=5, pady=5)
    TTS_m1_frame.tkraise()
    # Iniciar la aplicación
    root.mainloop()