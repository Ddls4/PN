topic = "Python"
topic2 = "Python/N"
nom = ""

def topicos(topicos, msg):
    if topicos == topic2:
        global nom
        nom = msg.payload.decode("utf-8")
        print(f"Hola, {nom}")
    
    if topicos == topic:
        if msg.payload == b'si':
            print(f"Hola, {nom}")
        elif msg.payload == b'no':
            print(f"Chau, {nom}")
        else:
            print(msg.payload)

