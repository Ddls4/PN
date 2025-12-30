import pyttsx3
import keyboard

engine = pyttsx3.init()

with open("texto.txt", "r", encoding="utf-8") as file:
    text = file.read()

engine.setProperty('volume', 1)

# Función de parada
def emergency_stop():
    print("¡Botón de emergencia activado!")
    engine.stop()   # detiene pyttsx3

print("Presiona ESC para detener la lectura")

# Detecta la tecla en un hilo aparte
keyboard.add_hotkey('esc', emergency_stop)

engine.say(text)
engine.runAndWait()
