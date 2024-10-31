import json
import time
from flask import Flask, jsonify, request
import paho.mqtt.client as mqtt

app = Flask(__name__)

# Variável global para armazenar os dados recebidos do MQTT
mqtt_data = {}

# Função de callback chamada quando a conexão MQTT é estabelecida
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscreva no tópico desejado
    client.subscribe("projeto_integrado/SENAI134/Cienciadedados/GrupoX") #TOPICO QUE O ESP32 ESTARÁ PUBLICANDO

# Função de callback chamada quando uma mensagem é recebida
def on_message(client, userdata, msg):
    global mqtt_data
    payload = msg.payload.decode('utf-8')
    mqtt_data = json.loads(payload)
    print(f"Received message: {mqtt_data}")

# Configure o cliente MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("test.mosquitto.org", 1883, 60) #SERVIDOR PUBLICO

# Função para iniciar o loop MQTT em uma thread separada
def start_mqtt():
    mqtt_client.loop_start()

# Endpoint para obter os dados mais recentes
@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(mqtt_data)

if __name__ == '__main__':
    start_mqtt()
    app.run(host='0.0.0.0', port=5000)
