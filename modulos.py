import subprocess
from deep_translator import GoogleTranslator
import pyttsx3
import pytesseract
import pyautogui
import speech_recognition as sr
import cv2
import numpy as np

# Configuración de pytesseract
pytesseract.pytesseract.tesseract_cmd = r'D:\10\Tesseract-OCR\Tesseract'

# Esta función ejecuta un comando en la terminal y devuelve el resultado.
# Puedes usarla para ejecutar comandos como 'cd', 'dir', 'start', etc.
# r'start C:\Users\clisb\OneDrive\Escritorio\Prog\Steam' 
def cmd(comando):
    resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
    return resultado
# Traducir texto
def Traducir(Texto, idioma_destino='es'):
    translated_text = GoogleTranslator(source='auto', target=idioma_destino)
    return translated_text.translate(Texto)
# Texto a voz
def Pronunciar(Texto, Volumen=1):
    engine = pyttsx3.init()
    engine.setProperty('volume', Volumen) # Establece el volumen (0.0 a 1.0)
    engine.say(Texto)
    engine.runAndWait()
# Extraer texto de imagenes   
def exxtreer_texto(imagen):
    text = pytesseract.image_to_string(imagen)
    return text
# Tomar captura  de patalla
def screenshot_and_extract_text(entry_x, entry_y, entry_ancho, entry_alto):
    region = (int(entry_x.get()), int(entry_y.get()), int(entry_ancho.get()) - int(entry_x.get()), int(entry_alto.get()) - int(entry_y.get()))
    screenshot = pyautogui.screenshot(region=region)
    text = exxtreer_texto(screenshot)
    return screenshot, text
# Voz a texto
def voz_a_texto():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Escuchando...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language='es-ES')
            print("Texto reconocido:", text)
            return text
        except sr.UnknownValueError:
            print("No se pudo entender el audio")
            return None
        except sr.RequestError as e:
            print(f"Error al solicitar resultados del servicio de reconocimiento de voz: {e}")
            return None
# Voz a texto con pyautogui para escribir el texto reconocido
def voz_a_texto_autogui():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Escuchando...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language='es-ES')
            print("Texto reconocido:", text)
            pyautogui.write(text, interval=0.01)  # Escribe el texto reconocido
        except sr.UnknownValueError:
            print("No se pudo entender el audio")
        except sr.RequestError as e:
            print(f"Error al solicitar resultados del servicio de reconocimiento de voz: {e}")

# OpenCV para filtros de color a partir de una cámara IP
class VideoFilter:
    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source)
        self.lower_bound = np.array([0, 0, 0])
        self.upper_bound = np.array([255, 255, 255])

    def set_bounds(self, lower, upper):
        self.lower_bound = np.array(lower)
        self.upper_bound = np.array(upper)

    def get_filtered_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        mask = cv2.inRange(frame, self.lower_bound, self.upper_bound)
        result = cv2.bitwise_and(frame, frame, mask=mask)
        return result

    def release(self):
        self.cap.release()


