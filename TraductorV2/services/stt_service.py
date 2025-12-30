import speech_recognition as sr

_recognizer = sr.Recognizer()

def escuchar(microfono, lang):
    with microfono as source:
        _recognizer.adjust_for_ambient_noise(source, duration=0.6)
        audio = _recognizer.listen(source)
        return _recognizer.recognize_google(audio, language=lang)
