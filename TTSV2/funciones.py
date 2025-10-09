from tkinter import *
from tkinter import filedialog

import os
from deep_translator import GoogleTranslator
import pyttsx3
import pytesseract
import time
import pyautogui
from pynput.mouse import Listener


# ---------------- CAMABIAR LA RUTA a una manual -------------------
engine = pyttsx3.init()
def tesseract_pach(txtt):
    config_file = "config.txt"

    # Si existe un archivo de configuración, cargar la ruta guardada
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            saved_path = file.read().strip()
        if os.path.isfile(saved_path):
            pytesseract.pytesseract.tesseract_cmd = saved_path
            txtt.configure(text=f"Ruta cargada")
            return
        else:
            txtt.configure(text="Ruta guardada no válida. Selecciona una nueva.")

    # Si no existe el archivo o la ruta guardada no es válida, pedir al usuario
    path = filedialog.askopenfilename(filetypes=[
        ("Ejecutables", "*.exe"),
        ("Todos los archivos", "*.*")
    ])
    if len(path) > 0 and os.path.isfile(path):
        pytesseract.pytesseract.tesseract_cmd = path
        txtt.configure(text=f"Ruta guardada")
        # Guardar la ruta en el archivo config.txt
        with open(config_file, "w") as file:
            file.write(path)
    else:
        txtt.configure(text="No seleccionaste un archivo válido.")
      

def Captura_Pantalla(entry_x, entry_y, entry_ancho, entry_alto):
    region = (int(entry_x.get()), int(entry_y.get()), int(entry_ancho.get()) - int(entry_x.get()), int(entry_alto.get()) - int(entry_y.get()))
    screenshot = pyautogui.screenshot(region=region)
    text = pytesseract.image_to_string(screenshot)
    return screenshot, text 
# TraducirTexto(text, entry_lang.get())
def TraducirTexto(entry_x_cap, idioma_destino='es'): 
    translated_text = GoogleTranslator(source='auto', target=idioma_destino)
    return translated_text.translate(entry_x_cap)
def Pronunciar(translated_text, entry_vol_cap=1):
        engine.setProperty('volume',entry_vol_cap)
        engine.say(translated_text)
        engine.runAndWait()
def insertar_texto(texto_traducido, text_area):
        text_area.delete("1.0", END)
        text_area.insert("1.5", texto_traducido)
        
def marca_posicion():
        time.sleep(3)
        x, y = pyautogui.position()
        return x, y

