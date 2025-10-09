# Modo 2
import tkinter as tk
import customtkinter as ctk

from funciones import marca_posicion, Captura_Pantalla, TraducirTexto, insertar_texto,Pronunciar
from pynput.mouse import Listener
import threading
import time
import keyboard

import cv2
from PIL import ImageTk
from PIL import Image

def TTSm2_frame(container):
    frame = tk.Frame(container)
    frame.place(relwidth=1, relheight=1)
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
            screenshot.save("screenshot.png")
            texto_traducido = TraducirTexto(text, language_combobox.get())
            insertar_texto(texto_traducido, text_area)
            if keyboard.is_pressed('w'):
                print("¡Has presionado 'w'!")
                Pronunciar(texto_traducido)
    def start_Pronunciar():
        thread = threading.Thread(target=Pronunciar(texto_traducido,(int(entry_volume.get())/ 100)))
        thread.daemon = True
        thread.start() 

    def op(): 
        global panelA
        text_area.configure(width=400, height=300)
        ruta_imagen = "screenshot.png" 
        imagen_original = Image.open(ruta_imagen)
        imagen_redimensionada = imagen_original.resize((400, 300))
        image = ImageTk.PhotoImage(imagen_redimensionada)
        # Verificar si el Label ya existe, y borrar su contenido previo si es necesario
         
        if 'panelA' in globals() and panelA is not None:
            panelA.config(image="")
            panelA.image = None
        panelA = tk.Label(content_frame, image=image)
        panelA.image = image
        panelA.grid(column=3, row=0, rowspan=2, padx=5, pady=5)
        
    content_frame = frame
    #--------------

    # Contenedor de configuración
    config_frame = ctk.CTkFrame(content_frame, width=300, height=200)
    config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

    config_label = ctk.CTkLabel(config_frame, text="Configuración", font=("Arial", 14))
    config_label.grid(row=0, column=0, columnspan=2, pady=5)

    # Campos para x, y, ancho, alto
    entry_x = ctk.CTkEntry(config_frame, placeholder_text="x")
    entry_x.grid(row=1, column=0, padx=5, pady=5)

    entry_ancho = ctk.CTkEntry(config_frame, placeholder_text="ancho")
    entry_ancho.grid(row=1, column=1, padx=5, pady=5)

    entry_y = ctk.CTkEntry(config_frame, placeholder_text="y")
    entry_y.grid(row=2, column=0, padx=5, pady=5)

    entry_alto = ctk.CTkEntry(config_frame, placeholder_text="alto")
    entry_alto.grid(row=2, column=1, padx=5, pady=5)

    # Botones xy, aa y DC
    btn_xy = ctk.CTkButton(config_frame, text="xy", command=marca1)
    btn_xy.grid(row=3, column=0, padx=5, pady=5)

    btn_aa = ctk.CTkButton(config_frame, text="aa", command=marca2)
    btn_aa.grid(row=3, column=1, padx=5, pady=5)

    btn_dc = ctk.CTkButton(config_frame, text="DC", width=250, command=marca)
    btn_dc.grid(row=4, column=0, columnspan=2, pady=5)


    # Contenedor de volumen y lenguaje
    settings_frame = ctk.CTkFrame(content_frame, width=300, height=100)
    settings_frame.grid(row=1, column=0, padx=10, pady=10, sticky="n")
    
    volume_label = ctk.CTkLabel(settings_frame, text="Volumen")
    volume_label.grid(row=0, column=0, padx=5)
    entry_volume = ctk.CTkSlider(settings_frame, from_=0, to=100, width=140) 
    entry_volume.grid(row=0, column=1, padx=5, pady=5)
    entry_volume.set(100)
    language_label = ctk.CTkLabel(settings_frame, text="Lenguaje")
    language_label.grid(row=1, column=0, padx=5, pady=5)
    language_combobox = ctk.CTkComboBox(settings_frame, values=["es", "en", "fr"])
    language_combobox.set("es")
    language_combobox.grid(row=1, column=1, padx=5, pady=5)

    btn_capture = ctk.CTkButton(settings_frame, text="captura", command=start_thread)
    btn_capture.grid(row=2, column=0,padx=5, pady=10)

    btn_tts = ctk.CTkButton(settings_frame, text="TTS", command=start_Pronunciar)
    btn_tts.grid(row=2, column=1,padx=5, pady=10)

    btnv = ctk.CTkButton(settings_frame, text="Elegir", width=250, command=op)
    btnv.grid(column=0,row=3, columnspan=2)

    # Contenedor de texto
    text_frame = ctk.CTkFrame(content_frame, width=400, height=300)
    text_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

    text_area = ctk.CTkTextbox(text_frame, width=800, height=300)
    text_area.pack(fill="both", expand=True, padx=10, pady=10)

    #--------------








    return frame