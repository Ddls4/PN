# Funciones/Traductor_Funciones.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import threading
import queue
import json
import os
import sys

# TTS / STT / Traducción online
import pyttsx3
from deep_translator import GoogleTranslator


# ---------------------------
# TTS engine (pyttsx3)
# ---------------------------
tts_engine = pyttsx3.init()
tts_lock = threading.Lock()
tts_stop_flag = threading.Event()

def choose_voice_for_language(lang_code):
    voices = tts_engine.getProperty('voices')
    lang_code = (lang_code or "").lower()
    for v in voices:
        name = (v.name or "").lower()
        idstr = (v.id or "").lower()
        if lang_code == 'es' and ('spanish' in name or 'es_' in idstr or 'es-' in idstr):
            return v.id
        if lang_code == 'en' and ('english' in name or 'en_' in idstr or 'en-' in idstr):
            return v.id
        if lang_code == 'pt' and ('portuguese' in name or 'pt_' in idstr or 'pt-' in idstr):
            return v.id
        if lang_code == 'it' and ('italian' in name or 'it_' in idstr or 'it-' in idstr):
            return v.id
    return None

def speak_text(text, lang_code, on_finished=None):
    def _run():
        with tts_lock:
            try:
                tts_stop_flag.clear()
                voice = choose_voice_for_language(lang_code)
                if voice:
                    tts_engine.setProperty('voice', voice)
                tts_engine.setProperty('volume', 1.0)
                tts_engine.say(text)
                tts_engine.runAndWait()
            except Exception as e:
                print("TTS error:", e)
            finally:
                if on_finished:
                    try:
                        on_finished()
                    except:
                        pass
    threading.Thread(target=_run, daemon=True).start()

def stop_tts():
    with tts_lock:
        try:
            tts_stop_flag.set()
            tts_engine.stop()
        except Exception as e:
            print("Error stopping TTS:", e)

# ---------------------------
# Traducción online
# ---------------------------
def traducir_texto_online(texto, idioma_origen, idioma_destino):
    try:
        if not texto.strip():
            return ""
        src = idioma_origen if idioma_origen and idioma_origen != 'auto' else 'auto'
        return GoogleTranslator(source=src, target=idioma_destino).translate(texto)
    except Exception as e:
        print("Error traducción online:", e)
        return "[Error traducción]"

