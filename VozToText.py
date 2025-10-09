"""
tkinter con poo que pueda usar el micrófono con speech_recognition y que lo escriba con pyautogui 
en donde este el click. la interfaz sea una texto de que hace la aplicación 1 botón para encender 
la escucha y otro para apagarla.
Y Algunos comandos especiales como abrir google, youtube, cerrar la aplicación.
"""
# iomportar librerias necesarias
import tkinter as tk
from tkinter import messagebox
import threading
import speech_recognition as sr
import pyautogui
import pyperclip
import webbrowser

# Definir la clase principal de la aplicación
# que maneja la interfaz gráfica y la lógica de reconocimiento de voz
class SpeechToTextApp:
    def __init__(self, root):
        # Inicializar la ventana principal y los componentes
        self.root = root
        self.root.title("Dictado por Voz Automático")
        self.is_listening = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.create_widgets()

    # Método para crear los widgets de la interfaz
    # Incluye etiquetas, botones y sus respectivas funciones
    def create_widgets(self):
        self.label = tk.Label(
            self.root,
            text="Esta aplicación convierte tu voz en texto\ny lo escribe donde esté el cursor.",
            font=("Arial", 12),
            padx=10, pady=10
        )
        self.label.pack()

        self.start_button = tk.Button(
            self.root, text="🎙️ Iniciar Escucha", command=self.start_listening, bg="green", fg="white", width=20
        )
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(
            self.root, text="🛑 Detener Escucha", command=self.stop_listening, bg="red", fg="white", width=20
        )
        self.stop_button.pack(pady=5)

    # Método para iniciar la escucha del micrófono
    # Crea un hilo para escuchar en segundo plano y evitar bloquear la interfaz
    def start_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.thread = threading.Thread(target=self.listen)
            self.thread.start()
            messagebox.showinfo("Escuchando", "La escucha ha comenzado.")
    # Método para detener la escucha del micrófono
    # Cambia el estado de escucha y muestra un mensaje
    def stop_listening(self):
        if self.is_listening:
            self.is_listening = False
            messagebox.showinfo("Escucha detenida", "La escucha ha sido detenida.")
    # Método que maneja la escucha del micrófono
    # Utiliza el reconocimiento de voz para convertir audio en texto
    def listen(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.is_listening:
                try:
                    print("Escuchando...")
                    audio = self.recognizer.listen(source, timeout=5)
                    text = self.recognizer.recognize_google(audio, language="es-ES")
                    print(f"Reconocido: {text}")

                    if text.lower().startswith("Hola") or text.lower().startswith("hola"):
                        comando = text[4:].strip().lower()
                        print(f"Comando especial detectado: {comando}")
                        
                        # Ejemplos de comandos especiales
                        if comando == "google":
                            webbrowser.open("https://www.google.com")
                        elif comando == "youtube":
                            webbrowser.open("https://www.youtube.com")
                        elif comando == "cerrar":
                            self.stop_listening()
                            self.root.quit()
                        else:
                            print("Comando no reconocido.")
                    else:
                        # Si no es un comando especial, escribe el texto en la ubicación actual del cursor
                        pyperclip.copy(text + " ")
                        pyautogui.hotkey('ctrl', 'v')

                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    print("No se entendió el audio.")
                except sr.RequestError as e:
                    print(f"Error con el servicio de reconocimiento: {e}")
                    break

# Crear la ventana principal y ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechToTextApp(root)
    root.mainloop()