# Modo 1
import tkinter as tk
import customtkinter as ctk

from funciones import marca_posicion, Captura_Pantalla, TraducirTexto, insertar_texto,Pronunciar
from pynput.mouse import Listener
import threading
import time
import keyboard

def TTSm1_frame(container):
    # Nota: Si en un boton poners argumentos lo usara al instante 
    def marca1():
        entry_x.delete(0, 'end')
        entry_y.delete(0, 'end')
        x, y = marca_posicion()
        entry_x.insert(0, x)
        entry_y.insert(0, y)
    def marca2():
        entry_ancho.delete(0, 'end')
        entry_alto.delete(0, 'end')
        x, y = marca_posicion()
        entry_ancho.insert(0, x)
        entry_alto.insert(0, y)
    # ---------------- CAMABIAR: Modularisar esto coord_inicial, coord_final = none -------------------
    def on_click(x, y,button, pressed):
        global coord_inicial, coord_final  
        if pressed:
            if coord_inicial is None:
                print(f"Coordenadas iniciales: {x}, {y}")
                coord_inicial = (x, y)
            else:
                print(f"Coordenadas finales: {x}, {y}")
                coord_final = (x, y)
                return False 
    def marca(): 
        global coord_inicial, coord_final 
        coord_inicial = None
        coord_final = None
        with Listener(on_click=on_click) as listener:
            listener.join()
        if coord_inicial is not None and coord_final is not None:
            entry_x.delete(0, 'end')
            entry_y.delete(0, 'end')
            entry_ancho.delete(0, 'end')
            entry_alto.delete(0, 'end')
            entry_x.insert(0, coord_inicial[0])
            entry_y.insert(0, coord_inicial[1])
            entry_ancho.insert(0, coord_final[0])
            entry_alto.insert(0, coord_final[1])
        else:
            print("Error: No se completó la selección de coordenadas.")
    # --- Loop 
    def start_thread():
            thread = threading.Thread(target=run_while_true)
            thread.daemon = True
            thread.start()
    def run_while_true():
        global texto_traducido
        texto_traducido = ""
        while True:
            if keyboard.is_pressed('q'):
                print("¡Has presionado 'q'! Saliendo del bucle...")
                insertar_texto("Saliendo del bucle...", text_area)
                break
            screenshot, text = Captura_Pantalla(entry_x, entry_y, entry_ancho, entry_alto)
            texto_traducido = TraducirTexto(text, entry_lang.get())
            insertar_texto(texto_traducido, text_area)
            if keyboard.is_pressed('w'):
                print("¡Has presionado 'w'!")
                Pronunciar(texto_traducido)
    def start_Pronunciar():
        thread = threading.Thread(target=Pronunciar(texto_traducido,(int(entry_vol.get())/ 100)))
        thread.daemon = True
        thread.start() 
    frame = tk.Frame(container)
    frame.place(relwidth=1, relheight=1)
    # ---------------------------------interfaz gráfica-----------------------------
    titulo = ctk.CTkLabel(frame, text="configuracion de la captura | presionado 'q' para Salir del bucle")
    titulo.grid(row=0 , column=0, columnspan=4)
    # ----- ROW 1 y 2 -----
    entry_x = ctk.CTkEntry(frame, placeholder_text="X")
    entry_x.grid(row=1, column=0, padx=5, pady=5)
    entry_y = ctk.CTkEntry(frame, placeholder_text="Y")
    entry_y.grid(row=2, column=0, padx=5, pady=5)
    Boton_XY = ctk.CTkButton(frame, text="XY",command=marca1, width=50, height=50).grid(row=1, column=1, rowspan=2)
    entry_ancho = ctk.CTkEntry(frame, placeholder_text="Ancho")
    entry_ancho.grid(row=1, column=2, padx=5, pady=5)
    entry_alto = ctk.CTkEntry(frame, placeholder_text="Alto")
    entry_alto.grid(row=2, column=2, padx=5, pady=5)
    Boton_AA = ctk.CTkButton(frame, text="AA",command=marca2, width=50, height=50).grid(row=1, column=3, rowspan=2)
    # ----- ROW 3 -----
    Boton_DC = ctk.CTkButton(frame, text="doble cap", command=marca, width=400, height=10).grid(row=3, column=0, columnspan=4)
    
    # ROW 4 y 5 |   sticky="w"
    ctk.CTkLabel(frame, text="Volumen").grid(row=4, column=0)
    entry_vol = ctk.CTkEntry(frame)
    entry_vol.grid(row=5, column=0)
    entry_vol.insert(0,"100")
    # Secion traducion
    ctk.CTkLabel(frame, text="Lenguaje").grid(row=4, column=2)
    entry_lang = ctk.CTkComboBox(frame,values=['en', 'it', 'es', 'ja', 'pt'])
    entry_lang.grid(row=5, column=2)
    entry_lang.set("es")  # valor inicial
    # ----------------------------------- Widget de Texto -----------------------------------
    ctk.CTkLabel(frame, text="Texto-Traducion").grid(row=6, column=0, columnspan=4)
    text_area = tk.Text(frame, width=55, height=10)
    text_area.grid(row=7, column=0, columnspan=4, padx=10, pady=5)
    # ----------------------------------- Botones de Captura y TTS -----------------------------------
    Boton_Captura = ctk.CTkButton(frame, text="Captura",command=start_thread, width=200) # command=start_thread
    Boton_Captura.grid(row=8, column=0,columnspan=2, padx=5, pady=5)
    Boton_TTS = ctk.CTkButton(frame, text="TTS",command=start_Pronunciar, width=200) # command=tts_lol
    Boton_TTS.grid(row=8, column=2, columnspan=2, padx=5, pady=5)

    return frame