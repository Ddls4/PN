from deep_translator import GoogleTranslator

def traducir_online(texto, src, dst):
    if not texto.strip():
        return ""
    src = src if src and src != 'auto' else 'auto'
    return GoogleTranslator(source=src, target=dst).translate(texto)