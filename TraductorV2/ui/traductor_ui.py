# ui/traductor_ui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue

from core.idiomas import LANG_OPTIONS, SR_LANG_MAP
from services.traduccion_service import traducir_online
from services.tts_service import speak, stop as stop_tts
from services.stt_service import escuchar
from services.historial_service import load as load_history, save as save_history

import speech_recognition as sr


class TraductorUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Traductor")
        self.root.geometry("1100x640")
        self.root.minsize(900, 520)

        # Estado
        self.queue = queue.Queue()
        self.history = load_history()

        # STT
        self.recognizer = sr.Recognizer()
        try:
            self.microphone = sr.Microphone()
        except OSError:
            self.microphone = None

        # UI
        self._build_styles()
        self._build_layout()
        self._bind_events()

        self.root.after(120, self._process_queue)

    # =========================
    # UI BUILD
    # =========================
    def _build_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6)

    def _build_layout(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self._build_tab_online()

        self.status_var = tk.StringVar(value="Listo")
        ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor="w"
        ).pack(side=tk.BOTTOM, fill=tk.X)

    def _build_tab_online(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Online")

        # --- Top ---
        top = ttk.Frame(frame)
        top.pack(fill=tk.X, padx=8, pady=8)

        ttk.Label(top, text="Origen").grid(row=0, column=0, sticky="w")
        self.combo_src = ttk.Combobox(
            top,
            state="readonly",
            values=[f"{n} ({c})" for n, c in LANG_OPTIONS],
            width=22
        )
        self.combo_src.current(0)
        self.combo_src.grid(row=1, column=0, padx=(0, 10))

        ttk.Label(top, text="Destino").grid(row=0, column=1, sticky="w")
        self.combo_dst = ttk.Combobox(
            top,
            state="readonly",
            values=[f"{n} ({c})" for n, c in LANG_OPTIONS],
            width=22
        )
        self.combo_dst.current(1)
        self.combo_dst.grid(row=1, column=1, padx=(10, 0))

        ttk.Button(
            top,
            text="Traducir",
            command=self.on_translate
        ).grid(row=1, column=2, padx=20)

        # --- Center ---
        center = ttk.Frame(frame)
        center.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.txt_src = self._create_textbox(center, "Origen")
        self.txt_dst = self._create_textbox(center, "Destino")

        # --- Bottom buttons ---
        bottom = ttk.Frame(frame)
        bottom.pack(fill=tk.X, padx=8, pady=6)

        ttk.Button(
            bottom,
            text="🎤 Voz → Texto",
            command=self.on_voice_input
        ).pack(side=tk.LEFT)

        ttk.Button(
            bottom,
            text="🔊 Leer Destino",
            command=self.on_tts
        ).pack(side=tk.LEFT, padx=6)

        ttk.Button(
            bottom,
            text="⏹ Detener voz",
            command=stop_tts
        ).pack(side=tk.LEFT)

    def _create_textbox(self, parent, label):
        frame = ttk.Frame(parent)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)

        ttk.Label(frame, text=label).pack(anchor="w")
        txt = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            font=("Arial", 12)
        )
        txt.pack(fill=tk.BOTH, expand=True)
        return txt

    # =========================
    # EVENTS
    # =========================
    def _bind_events(self):
        self.root.bind("<Escape>", lambda e: stop_tts())

    def on_translate(self):
        text = self.txt_src.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Info", "No hay texto para traducir.")
            return

        src = self._get_src_code()
        dst = self._get_dst_code()

        self.status_var.set("Traduciendo...")
        threading.Thread(
            target=self._translate_bg,
            args=(text, src, dst),
            daemon=True
        ).start()

    def _translate_bg(self, text, src, dst):
        try:
            translated = traducir_online(text, src, dst)
            self.queue.put(("translated", (text, translated, src, dst)))
        except Exception as e:
            self.queue.put(("error", str(e)))

    def on_voice_input(self):
        if not self.microphone:
            messagebox.showwarning("Micrófono", "No se detectó micrófono.")
            return

        lang = SR_LANG_MAP.get(self._get_src_code(), "es-ES")
        self.status_var.set("Escuchando...")
        threading.Thread(
            target=self._voice_bg,
            args=(lang,),
            daemon=True
        ).start()

    def _voice_bg(self, lang):
        try:
            text = escuchar(self.microphone, lang)
            self.queue.put(("voice", text))
        except Exception as e:
            self.queue.put(("error", str(e)))

    def on_tts(self):
        text = self.txt_dst.get("1.0", tk.END).strip()
        if not text:
            return
        speak(text, self._get_dst_code())

    # =========================
    # QUEUE
    # =========================
    def _process_queue(self):
        try:
            while not self.queue.empty():
                tag, data = self.queue.get_nowait()

                if tag == "translated":
                    src, translated, src_code, dst_code = data
                    self.txt_dst.delete("1.0", tk.END)
                    self.txt_dst.insert(tk.END, translated)
                    self.history.insert(0, {
                        "src": src,
                        "translated": translated,
                        "src_code": src_code,
                        "dst_code": dst_code
                    })
                    save_history(self.history)
                    self.status_var.set("Listo")

                elif tag == "voice":
                    self.txt_src.insert(tk.END, " " + data)
                    self.status_var.set("Texto reconocido")

                elif tag == "error":
                    self.status_var.set("Error")
                    messagebox.showerror("Error", data)

        finally:
            self.root.after(120, self._process_queue)

    # =========================
    # HELPERS
    # =========================
    def _get_src_code(self):
        return self.combo_src.get().split("(")[-1].strip(")")

    def _get_dst_code(self):
        return self.combo_dst.get().split("(")[-1].strip(")")
