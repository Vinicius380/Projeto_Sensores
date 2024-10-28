from datetime import datetime, timezone
from flask import Flask, Response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import json
import paho.mqtt.client as mqtt

# pip install paho-mqtt flask -> Conexao com os sensores

# CONEXAO COM O BANCO DE DADOS

# Nome da aplicacao
app = Flask("registro")

# A conexao com o baco havera modificacoes na base de dados
app.config("SQLALCHEMY_TRACK_MODIFICATIONS") = False

# Confihura a URI de conexao com o banco de dados MySql.
app.config("SQLALCHEMY_DATABASE_URI") = "mysql://root:senai%40134@127.0.0.1/bd_medidor"

# Cria uma instancia do SQLAlchemy, passando a aplicacao Flak como parametro.
mybd = SQLAlchemy(app)

# CONEXAO DOS SENSORES
mqtt_dados = {}

def conexao_sensor(cliente, userdata, flags, ec):
    cliente.subscribe("projeto_integrado/SENAI134/Cienciadedados/GrupoX")

def msg_sensor(client, userdata, msg):
    global mqtt_dados
    # Decodificar a mensagem recebida de bytes para string
    valor = msg.payload.decode("utf-8")

    # Decodificar de string para JSON
    mqtt_dados = json.loads(valor)
    
    print(f"Mensagem Recebida: {mqtt_dados}")

    # Correlacao Banco de Dados com Sensores
    with app.app_context():
        try:
            temperatura = mqtt_dados.get("temperature")
            umidade = mqtt_dados.get("humidity")
            pressao = mqtt_dados.get("pressure")
            altitude = mqtt_dados.get("altitude")
            co2 = mqtt_dados.get("co2")
            poeira = 0
            tempo_registro = mqtt_dados.get("timestamp")

            if tempo_registro is None:
                print("Timestamp não encontrado")
                return

            try:
                 tempo_oficial = datetime.fromtimestamp(int (tempo_registro), tz=timezone.utc)
                
            except (ValueError, TypeError) as e:
                 print(f"Erro ao converter timestamp: {str(e)}")
                 return

# Criar o porjeto que vai simular a tabela do banco
            novos_dados = Registro(
                temperaturaV = temperatura,
                altitudeV = altitude,
                umidadeV = umidade,
                co2V = co2,
                poeiraV = poeira,
                tempo_registroV = tempo_oficial
            )

            # Adicionar novos registros ao banco

            mybd.session.add(novos_dados)
            mybd.session.commit()
            print("Dados foram inseridos com sucesso no banco de dados!")

        except Exception as e:
            print(f"Erro ao processar os dados do MQTT: {str(e)}")
            mybd.session.rollback()

mqtt_client = mqtt.Client()
mqtt_client.on_connect = conexao_sensor
mqtt_client.on_message = msg_sensor
mqtt_client.connect("test.mosquitto.org", 1883, 60)

def start_mqtt():
    mqtt_client.loop_start()

class Registro(mybd.Model):
    __tablename__ = "tb_registro"
    id = mybd.Column(mybd.Integer, primary_key=True, autoincrement=True)
    temperatura = mybd.Column(mybd.Numeric(10,2))
    pressao = mybd.Column(mybd.Numeric(10,2))
    altitude = mybd.Column(mybd.Numeric(10,2))
    umidade = mybd.Column(mybd.Numeric(10,2))
    co2 = mybd.Column(mybd.Numeric(10,2))
    poeira = mybd.Column(mybd.Numeric(10,2))
    tempo_registro = mybd.Column(mybd.Datetime)

# *******************************************

#******************GET***********************

@app.route("/registro", methods=["GET"])
def seleciona_registro():
    registro_objetos = Registro.query.all()
    registro_json = [registro.to_json() for registro in registro_objetos]
    return gera_resposta(200, "registro", registro_json)





def gera_resposta(status, nome_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_conteudo] = conteudo

    if(mensagem):
        body["mensagem"] = mensagem
    return Response(json.dumps(body), status=status, mimetype="application/json")
app.run(port=5000, host="localhost", degub=True)