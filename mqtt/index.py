import paho.mqtt.client as mqtt
from funciones import topicos
import time
# Config de MQTT
broker = "test.mosquitto.org"
port = 1883
topic = "Python"
topic2 = "Python/N"

def on_connect(client, userdata, flags, rc):
    print("Conectado con código de resultado: " + str(rc))
    client.subscribe(topic)
    client.subscribe(topic2)
    
# MQTT
def on_message(client, userdata, msg):
    client.publish("pcR", "y")
    print("Mensaje recivido:")
    print(f"Topic: [{msg.topic}] Mensaje: [{msg.payload.decode('utf-8')}]") 
    topicos(msg.topic, msg)
    

# Asignar los callbacks al cliente
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Conectar al broker
try:
    client.connect(broker, port)
    client.loop_forever()
except KeyboardInterrupt:
    print("Desconectado del broker.")
    client.publish("pcR", "n") 
    client.disconnect()