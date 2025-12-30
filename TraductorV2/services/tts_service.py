import pyttsx3
import threading

_engine = pyttsx3.init()
_lock = threading.Lock()

def speak(text, lang_code, on_finished=None):
    def run():
        with _lock:
            _engine.say(text)
            _engine.runAndWait()
            if on_finished:
                on_finished()
    threading.Thread(target=run, daemon=True).start()

def stop():
    with _lock:
        _engine.stop()

def get_voices():
    return _engine.getProperty('voices')
