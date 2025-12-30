import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import threading
import queue
import json
import os
import sys

# TTS / STT / Traducción online
import pyttsx3
import speech_recognition as sr
from deep_translator import GoogleTranslator

# Export DOCX
try:
    from docx import Document
    DOCX_AVAILABLE = True
except Exception:
    DOCX_AVAILABLE = False

# ---------------------------
# Config / Idiomas
# ---------------------------
LANG_OPTIONS = [
    ("Español", "es"),
    ("Inglés", "en"),
    ("Portugués", "pt"),
    ("Italiano", "it"),
]

SR_LANG_MAP = {
    'es': 'es-ES',
    'en': 'en-US',
    'pt': 'pt-PT',
    'it': 'it-IT',
}

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



# ---------------------------
# App principal
# ---------------------------
HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".traductor_history.json")

class TraductorApp:
    def __init__(self, root):
        self.root = root
        root.title("Traductor - Completo")
        root.geometry("1100x640")
        root.minsize(900, 520)

        # Cola hilos
        self.q = queue.Queue()

        # STT
        self.recognizer = sr.Recognizer()
        try:
            self.microphone = sr.Microphone()
        except Exception as e:
            self.microphone = None
            print("Mic error:", e)

        # Historial (lista de dicts: {src_lang, dst_lang, src_text, translated})
        self.history = []
        self.load_history()

        # Modo oscuro flag
        self.dark_mode = False

        # Estilos
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.setup_styles()

        # Crear notebook (pestañas)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.create_tab_online()
        self.create_tab_settings()

        # Status bar
        self.status_var = tk.StringVar(value="Listo")
        status = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        status.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind
        root.bind_all("<Escape>", lambda e: stop_tts())
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        root.after(120, self.process_queue)

    # ---------------------------
    # Styles
    # ---------------------------
    def setup_styles(self):
        # Baseline button style
        self.style.configure('TButton', padding=6, font=('Segoe UI', 10))
        self.style.configure('Primary.TButton', background='#1976D2', foreground='white')
        self.style.map('Primary.TButton', background=[('active', '#1565C0')])
        self.style.configure('Danger.TButton', background='#D32F2F', foreground='white')

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            # Colors for dark mode (simple)
            self.style.configure('.', background='#2b2b2b', foreground='#e6e6e6')
            self.style.configure('TLabel', background='#2b2b2b', foreground='#e6e6e6')
            self.style.configure('TFrame', background='#2b2b2b')
            self.style.configure('TButton', background='#3c3f41', foreground='#e6e6e6')
        else:
            # revert (light)
            self.style.configure('.', background='#f0f0f0', foreground='black')
            self.style.configure('TLabel', background='#f0f0f0', foreground='black')
            self.style.configure('TFrame', background='#f0f0f0')
            self.style.configure('TButton', background='#f0f0f0', foreground='black')

    # ---------------------------
    # Tab: Online
    # ---------------------------
    def create_tab_online(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Online")

        # Top: combos + control buttons
        top = ttk.Frame(frame)
        top.pack(fill=tk.X, padx=8, pady=8)

        ttk.Label(top, text="Idioma origen:").grid(row=0, column=0, sticky='w')
        self.combo_src = ttk.Combobox(top, state='readonly', width=22)
        self.combo_src['values'] = [f"{n} ({c})" for n, c in LANG_OPTIONS]
        self.combo_src.current(0)
        self.combo_src.grid(row=1, column=0, padx=(0,10))

        ttk.Label(top, text="Idioma destino:").grid(row=0, column=1, sticky='w', padx=(12,0))
        self.combo_dst = ttk.Combobox(top, state='readonly', width=22)
        self.combo_dst['values'] = [f"{n} ({c})" for n, c in LANG_OPTIONS]
        self.combo_dst.current(1)
        self.combo_dst.grid(row=1, column=1, padx=(12,0))

        btns = ttk.Frame(top)
        btns.grid(row=0, column=2, rowspan=2, padx=(18,0), sticky='e')
        ttk.Button(btns, text="↔️ Intercambiar", command=self.on_swap).grid(row=0, column=0, padx=4)
        ttk.Button(btns, text="↔️ Traducir", style='Primary.TButton', command=self.on_translate_online).grid(row=0, column=1, padx=4)
        ttk.Button(btns, text="🧹 Limpiar", command=self.on_clear_online).grid(row=0, column=2, padx=4)
        ttk.Button(btns, text="📄 Exportar Word", command=self.on_export_word).grid(row=0, column=3, padx=4)
        ttk.Button(btns, text="📜 Historial", command=self.show_history).grid(row=0, column=4, padx=4)

        # Center: two textboxes
        center = ttk.Frame(frame)
        center.pack(fill=tk.BOTH, expand=True, padx=8, pady=(2,8))

        left = ttk.Frame(center)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,6))

        ttk.Label(left, text="Origen").pack(anchor='w')
        self.txt_origen = scrolledtext.ScrolledText(left, wrap=tk.WORD, font=('Arial', 12), height=18)
        self.txt_origen.pack(fill=tk.BOTH, expand=True, pady=(6,6))

        left_btns = ttk.Frame(left)
        left_btns.pack(anchor='w', pady=(0,6))
        ttk.Button(left_btns, text="🎤 Voice→Text (Origen)", command=self.on_voice_origen).grid(row=0, column=0, padx=(0,6))
        ttk.Button(left_btns, text="🔊 Leer Origen", command=lambda: self.on_tts(self.txt_origen, self.get_src_code())).grid(row=0, column=1, padx=(0,6))

        right = ttk.Frame(center)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6,0))

        ttk.Label(right, text="Destino").pack(anchor='w')
        self.txt_dest = scrolledtext.ScrolledText(right, wrap=tk.WORD, font=('Arial', 12), height=18)
        self.txt_dest.pack(fill=tk.BOTH, expand=True, pady=(6,6))

        right_btns = ttk.Frame(right)
        right_btns.pack(anchor='w', pady=(0,6))
        ttk.Button(right_btns, text="🔊 Leer Destino", command=lambda: self.on_tts(self.txt_dest, self.get_dst_code())).grid(row=0, column=0, padx=(0,6))

    # ---------------------------
    # Tab: Settings
    # ---------------------------
    def create_tab_settings(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Configuración")

        ttk.Label(frame, text="Ajustes TTS / UI").pack(anchor='w', padx=8, pady=(8,2))
        settings = ttk.Frame(frame)
        settings.pack(fill=tk.X, padx=8, pady=4)

        # Dark mode toggle
        self.dark_var = tk.BooleanVar(value=self.dark_mode)
        ttk.Checkbutton(settings, text="Modo oscuro", variable=self.dark_var, command=self.on_toggle_dark).grid(row=0, column=0, sticky='w', padx=(0,6))

        # Mostrar voces disponibles (lista)
        ttk.Button(settings, text="Listar voces TTS", command=self.show_available_voices).grid(row=0, column=1, padx=(12,6))
        ttk.Label(settings, text="(Si la voz para ES/IT/PT no existe, el motor usará la voz por defecto)").grid(row=1, column=0, columnspan=2, sticky='w', pady=(6,0))

    # ---------------------------
    # Helpers / UI Actions
    # ---------------------------
    def get_src_code(self):
        sel = self.combo_src.get()
        return sel.split('(')[-1].strip(')') if sel else 'es'

    def get_dst_code(self):
        sel = self.combo_dst.get()
        return sel.split('(')[-1].strip(')') if sel else 'en'

    def on_swap(self):
        s_idx = self.combo_src.current()
        d_idx = self.combo_dst.current()
        self.combo_src.current(d_idx)
        self.combo_dst.current(s_idx)
        txt1 = self.txt_origen.get("1.0", tk.END)
        txt2 = self.txt_dest.get("1.0", tk.END)
        self.txt_origen.delete("1.0", tk.END)
        self.txt_dest.delete("1.0", tk.END)
        self.txt_origen.insert(tk.END, txt2)
        self.txt_dest.insert(tk.END, txt1)
        self.status_var.set("Intercambiado")

    def on_clear_online(self):
        self.txt_origen.delete("1.0", tk.END)
        self.txt_dest.delete("1.0", tk.END)
        self.status_var.set("Listo")

    # ---------------------------
    # Translate online
    # ---------------------------
    def on_translate_online(self):
        src_text = self.txt_origen.get("1.0", tk.END).strip()
        if not src_text:
            messagebox.showinfo("Info", "No hay texto en origen para traducir.")
            return
        src = self.get_src_code()
        dst = self.get_dst_code()
        self.status_var.set("Traduciendo (online)...")
        threading.Thread(target=self._translate_online_bg, args=(src_text, src, dst), daemon=True).start()

    def _translate_online_bg(self, text, src, dst):
        try:
            translated = traducir_texto_online(text, src, dst)
            # push to queue
            self.q.put(('online_translated', {'src': text, 'translated': translated, 'src_code': src, 'dst_code': dst}))
        except Exception as e:
            self.q.put(('error', str(e)))

    # ---------------------------
    # Voice -> Text (online origin)
    # ---------------------------
    def on_voice_origen(self):
        if not self.microphone:
            messagebox.showwarning("Micrófono", "No se detectó micrófono.")
            return
        recog_lang = SR_LANG_MAP.get(self.get_src_code(), 'es-ES')
        self.status_var.set(f"Escuchando ({recog_lang})...")
        threading.Thread(target=self._listen_bg, args=(recog_lang,), daemon=True).start()

    def _listen_bg(self, recog_lang):
        with self.microphone as source:
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=12)
                text = self.recognizer.recognize_google(audio, language=recog_lang)
                self.q.put(('recognized_online', text))
            except sr.WaitTimeoutError:
                self.q.put(('rec_error', "Timeout esperando audio"))
            except sr.UnknownValueError:
                self.q.put(('rec_error', "No se entendió el audio"))
            except sr.RequestError as e:
                self.q.put(('rec_error', f"Error servicio: {e}"))
            except Exception as e:
                self.q.put(('rec_error', str(e)))

    # ---------------------------
    # Voice -> Text (offline origin) - reuses recognizer but just place text in off_src
    # ---------------------------
    def on_voice_offline(self):
        if not self.microphone:
            messagebox.showwarning("Micrófono", "No se detectó micrófono.")
            return
        recog_lang = 'es-ES'  # podríamos pedir al usuario, por simplicidad dejamos es-ES
        self.status_var.set(f"Escuchando Offline ({recog_lang})...")
        threading.Thread(target=self._listen_off_bg, args=(recog_lang,), daemon=True).start()

    def _listen_off_bg(self, recog_lang):
        with self.microphone as source:
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=12)
                text = self.recognizer.recognize_google(audio, language=recog_lang)
                self.q.put(('recognized_offline', text))
            except sr.WaitTimeoutError:
                self.q.put(('rec_error', "Timeout esperando audio"))
            except sr.UnknownValueError:
                self.q.put(('rec_error', "No se entendió el audio"))
            except sr.RequestError as e:
                self.q.put(('rec_error', f"Error servicio: {e}"))
            except Exception as e:
                self.q.put(('rec_error', str(e)))

    # ---------------------------
    # TTS
    # ---------------------------
    def on_tts(self, widget, lang_code):
        text = widget.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Info", "No hay texto para leer.")
            return
        self.status_var.set("Leyendo...")
        speak_text(text, lang_code, on_finished=lambda: self.status_var.set("Listo"))

    # ---------------------------
    # Export to Word
    # ---------------------------
    def on_export_word(self):
        if not DOCX_AVAILABLE:
            messagebox.showwarning("DOCX", "python-docx no está instalado. Ejecutá 'pip install python-docx' para habilitar exportar a Word.")
            return
        # Preguntar si exportar origen o destino o ambos
        choice = messagebox.askquestion("Exportar", "Exportar texto DESTINO a Word?\n\nSi elegís 'No' se exportará ORIGEN.")
        if choice == 'yes':
            txt = self.txt_dest.get("1.0", tk.END).strip()
            default_name = "traduccion_destino.docx"
        else:
            txt = self.txt_origen.get("1.0", tk.END).strip()
            default_name = "traduccion_origen.docx"
        if not txt:
            messagebox.showinfo("Info", "No hay texto para exportar.")
            return
        filename = simpledialog.askstring("Guardar como", "Nombre archivo (.docx):", initialvalue=default_name)
        if not filename:
            return
        if not filename.lower().endswith(".docx"):
            filename += ".docx"
        try:
            doc = Document()
            doc.add_paragraph(txt)
            doc.save(filename)
            messagebox.showinfo("OK", f"Archivo guardado: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    # ---------------------------
    # Historial
    # ---------------------------
    def add_history(self, src_text, translated, src_code, dst_code):
        item = {
            "src": src_text,
            "translated": translated,
            "src_code": src_code,
            "dst_code": dst_code
        }
        self.history.insert(0, item)
        # Limitar a 200 entradas
        self.history = self.history[:200]
        self.save_history()

    def save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Error saving history:", e)

    def load_history(self):
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
        except Exception as e:
            print("Error loading history:", e)
            self.history = []

    def show_history(self):
        win = tk.Toplevel(self.root)
        win.title("Historial de traducciones")
        win.geometry("700x500")
        frm = ttk.Frame(win)
        frm.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        lb = tk.Listbox(frm)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(frm, orient=tk.VERTICAL, command=lb.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        lb.config(yscrollcommand=scrollbar.set)

        for i, item in enumerate(self.history):
            summary = f"{i+1}: {item.get('src_code','?')}→{item.get('dst_code','?')} • {item.get('src','')[:60].replace('\\n',' ')}..."
            lb.insert(tk.END, summary)

        def on_select(evt):
            sel = lb.curselection()
            if not sel: return
            idx = sel[0]
            item = self.history[idx]
            self.txt_origen.delete("1.0", tk.END)
            self.txt_origen.insert(tk.END, item.get('src',''))
            self.txt_dest.delete("1.0", tk.END)
            self.txt_dest.insert(tk.END, item.get('translated',''))
            win.destroy()

        lb.bind('<<ListboxSelect>>', on_select)
        ttk.Button(win, text="Cerrar", command=win.destroy).pack(pady=6)

    # ---------------------------
    # Voices list
    # ---------------------------
    def show_available_voices(self):
        voices = tts_engine.getProperty('voices')
        win = tk.Toplevel(self.root)
        win.title("Voces disponibles")
        win.geometry("600x320")
        txt = scrolledtext.ScrolledText(win, wrap=tk.WORD, height=18)
        txt.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        for v in voices:
            txt.insert(tk.END, f"ID: {v.id}\nName: {v.name}\nLang: {getattr(v, 'languages', None)}\n\n")
        txt.configure(state=tk.DISABLED)

    # ---------------------------
    # Queue processing
    # ---------------------------
    def process_queue(self):
        try:
            while not self.q.empty():
                tag, payload = self.q.get_nowait()
                if tag == 'online_translated':
                    data = payload
                    self.txt_dest.delete("1.0", tk.END)
                    self.txt_dest.insert(tk.END, data['translated'])
                    self.status_var.set("Listo (online)")
                    # agregar al historial
                    self.add_history(data['src'], data['translated'], data['src_code'], data['dst_code'])
                elif tag == 'offline_translated':
                    data = payload
                    self.off_dst.delete("1.0", tk.END)
                    self.off_dst.insert(tk.END, data['translated'])
                    self.status_var.set("Listo (offline)")
                elif tag == 'recognized_online':
                    text = payload
                    cur = self.txt_origen.get("1.0", tk.END).strip()
                    new = (cur + " " + text).strip() if cur else text
                    self.txt_origen.delete("1.0", tk.END)
                    self.txt_origen.insert(tk.END, new)
                    self.status_var.set("Reconocido (online)")
                elif tag == 'recognized_offline':
                    text = payload
                    cur = self.off_src.get("1.0", tk.END).strip()
                    new = (cur + " " + text).strip() if cur else text
                    self.off_src.delete("1.0", tk.END)
                    self.off_src.insert(tk.END, new)
                    self.status_var.set("Reconocido (offline)")
                elif tag == 'rec_error':
                    self.status_var.set(f"Error reconocimiento: {payload}")
                elif tag == 'error':
                    self.status_var.set(f"Error: {payload}")
        except Exception as e:
            print("process_queue:", e)
        finally:
            self.root.after(120, self.process_queue)

    # ---------------------------
    # Settings events
    # ---------------------------
    def on_toggle_dark(self):
        self.toggle_dark_mode()

    # ---------------------------
    # Close
    # ---------------------------
    def on_close(self):
        if messagebox.askokcancel("Salir", "¿Querés salir?"):
            try:
                stop_tts()
            except:
                pass
            self.save_history()
            self.root.destroy()

# ---------------------------
# Ejecutar app
# ---------------------------
def main():
    root = tk.Tk()
    app = TraductorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
