# pip install scikit-learn
# pip install tensorflow
# pip install matplotlib
# pip install paho-mqtt
# pip install paho-mqtt flask

import datetime
import json
from time import timezone
from flask import Flask
import google.generativeai as genai
import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
import numpy as np
import paho.mqtt.client as mqtt

# Desativar oneDNN no TensorFlow
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

genai.configure(api_key="AIzaSyChtbxglA_gwNop0FmeUrirEwxrE71dQXQ")

app = Flask('registro')
mqtt_data = {}
temperatura = None
model = None  # Definindo o modelo fora da função main

def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected with result code " + str(rc))
    client.subscribe("projeto_integrado/SENAI134/Cienciadedados/GrupoX")

def on_message(client, userdata, msg):
    global mqtt_data, temperatura
    payload = msg.payload.decode('utf-8')
    mqtt_data = json.loads(payload)
    print(f"Received message: {mqtt_data}")

    with app.app_context():
        temperatura = mqtt_data.get('temperature')
        pressao = mqtt_data.get('pressure')
        altitude = mqtt_data.get('altitude')
        umidade = mqtt_data.get('humidity')
        co2 = mqtt_data.get('CO2')
        timestamp_unix = mqtt_data.get('timestamp')

        # Verifica se a temperatura foi capturada corretamente
        if temperatura is not None:
            print(f"Temperatura recebida: {temperatura}")
            main()  # Chama a função main após receber a temperatura
        else:
            print("Temperatura não capturada corretamente.")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("test.mosquitto.org", 1883, 60)

def start_mqtt():
    mqtt_client.loop_start()

def main():
    global temperatura, model

    # Verifique se a temperatura foi atualizada
    if temperatura is None:
        print("Temperatura não está disponível.")
        return

    # Passo 1: Criar o DataFrame
    recomendacoes = ['Hidrate-se e use protetor solar', 'Roupas leves e hidrate-se',
                     'Vista-se adequadamente e beba algo quente', 'Roupas quentes e lugares abrigados']
    
    recomendacao_aleatoria = np.random.choice(recomendacoes)

    dados = {
        'Temperatura': [temperatura],  # Coloque a temperatura em uma lista
        'Recomendacao': [recomendacao_aleatoria]  # Use apenas uma recomendação
    }

    df = pd.DataFrame(dados)

    # Passo 2: Codificar as recomendações em números
    encoder = LabelEncoder()
    df['Recomendacao'] = encoder.fit_transform(df['Recomendacao'])

    # Separar em variáveis de entrada (X) e saída (y)
    X = df[['Temperatura']]
    y = df['Recomendacao']

    # Se o modelo ainda não estiver definido, crie e treine
    if model is None:
        # Passo 3: Construir o modelo
        model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(16, input_shape=[1], activation='relu'),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1, activation='linear')  # Saída de regressão linear
        ])

        # Compilar o modelo
        model.compile(optimizer='adam', loss='mse')

        # Treinar o modelo
        model.fit(X, y, epochs=50)

    # Passo 4: Fazer previsões
    temperatura_teste = np.array([[temperatura]])  # Coloque a temperatura em uma matriz 2D
    previsao = model.predict(temperatura_teste)

    # Decodificar a recomendação de volta para texto
    recomendacao_final = encoder.inverse_transform([int(np.round(previsao[0]))])
    print(f"A recomendação para a temperatura {temperatura} é: {recomendacao_final[0]}")

    # Chamada para a API Gemini
    try:
        generative_model = genai.GenerativeModel('gemini-1.5-flash')
        response = generative_model.generate_content(
            f"Com essa temperatura: {temperatura}C, a melhor recomendação é: {recomendacao_final[0]}?"
        )

        # Verificar se a resposta tem um campo 'content' ou 'text'
        if hasattr(response, 'content'):
            resposta = response.content
        elif hasattr(response, 'text'):
            resposta = response.text
        else:
            resposta = "Erro ao obter a resposta da API"
        
        print("Resposta da API Gemini:", resposta)

    except Exception as e:
        print(f"Erro ao chamar a API Gemini: {str(e)}")

if __name__ == '__main__':
    start_mqtt()
    app.run(debug=True)
