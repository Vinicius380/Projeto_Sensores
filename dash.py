import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
from query import *

# Consulta no banco de dados
query = "SELECT * FROM tb_registro"

# Carregar os dados no MySQL
df = conexao(query)

#Botao para atualizacao dos dados
if st.button("Atualizar Dados"):
    df = conexao(query)

# MENU LATERAL
st.sidebar.header("Selecione a informação para gerar o gráfico")

# Selecao de colunas X
colunaX = st.sidebar.selectbox(
    "Eixo X",
    options=["umidade", "temperatura", "pressao", "altitude", "co2", "poeira"],
    index=0
)

colunaY = st.sidebar.selectbox(
    "Eixo Y",
    options=["umidade", "temperatura", "pressao", "altitude", "co2", "poeira"],
    index=1
)

# Verificar quais os atributos do filtro
def filtros(atributo):
    return atributo in [colunaX, colunaY]

# Filtro de Range -> SLIDER
st.sidebar.header("Selecione o Filtro")


if filtros("umidade"):
    umidade_range = st.sidebar.slider(
        "Umidade",
        #Valor minimo
        min_value=float(df["umidade"].min()),
        #Valor maximo
        max_value=float(df["umidade"].max()),
        #Faixa de valores selecionados
        value= (float(df["umidade"].min()), float(df["umidade"].max())),
        #Incremento para cada movimento do slider
        step=0.1
    )


# Temperatura
if filtros("temperatura"):
    temperatura_range = st.sidebar.slider(
        "Temperatura (°C)",
        #Valor minimo
        min_value=float(df["temperatura"].min()),
        #Valor maximo
        max_value=float(df["temperatura"].max()),
        #Faixa de valores selecionados
        value= (float(df["temperatura"].min()), float(df["temperatura"].max())),
        #Incremento para cada movimento do slider
        step=0.1
    )

if filtros("pressao"):
    pressao_range = st.sidebar.slider(
        "Pressao",
        #Valor minimo
        min_value=float(df["pressao"].min()),
        #Valor maximo
        max_value=float(df["pressao"].max()),
        #Faixa de valores selecionados
        value= (float(df["pressao"].min()), float(df["pressao"].max())),
        #Incremento para cada movimento do slider
        step=0.1
    )

if filtros("altitude"):
    altitude_range = st.sidebar.slider(
        "Altitude",
        #Valor minimo
        min_value=float(df["altitde"].min()),
        #Valor maximo
        max_value=float(df["altitude"].max()),
        #Faixa de valores selecionados
        value= (float(df["altitude"].min()), float(df["altitude"].max())),
        #Incremento para cada movimento do slider
        step=0.1
    )

if filtros("co2"):
    co2_range = st.sidebar.slider(
        "Co2",
        #Valor minimo
        min_value=float(df["co2"].min()),
        #Valor maximo
        max_value=float(df["co2"].max()),
        #Faixa de valores selecionados
        value= (float(df["co2"].min()), float(df["co2"].max())),
        #Incremento para cada movimento do slider
        step=0.1
    )

if filtros("poeira"):
    poeira_range = st.sidebar.slider(
        "Poeira",
        #Valor minimo
        min_value=float(df["poeira"].min()),
        #Valor maximo
        max_value=float(df["poeira"].max()),
        #Faixa de valores selecionados
        value= (float(df["poeira"].min()), float(df["poeira"].max())),
        #Incremento para cada movimento do slider
        step=0.1
    )

df_selecionado = df.copy()
# Cria uma copia do df original


if filtros("umidade"):
    df_selecionado = df_selecionado[
    (df_selecionado["umidade"] >= umidade_range[0]) &
    (df_selecionado["umidade"] <= umidade_range[1])
    ]

if filtros("temperatura"):
    df_selecionado = df_selecionado[
    (df_selecionado["temperatura"] >= temperatura_range[0]) &
    (df_selecionado["temperatura"] <= temperatura_range[1])
    ]

if filtros("pressao"):
    df_selecionado = df_selecionado[
    (df_selecionado["pressao"] >= pressao_range[0]) &
    (df_selecionado["pressao"] <= pressao_range[1])
    ]

if filtros("altitude"):
    df_selecionado = df_selecionado[
    (df_selecionado["altitude"] >= altitude_range[0]) &
    (df_selecionado["altitude"] <= altitude_range[1])
    ]

if filtros("co2"):
    df_selecionado = df_selecionado[
    (df_selecionado["co2"] >= co2_range[0]) &
    (df_selecionado["co2"] <= co2_range[1])
    ]

if filtros("poeira"):
    df_selecionado = df_selecionado[
    (df_selecionado["poeira"] >= poeira_range[0]) &
    (df_selecionado["poeira"] <= poeira_range[1])
    ]


def Home():
    with st.expander("Tabela"):
        mostrarDados = st.multiselect(
            "Filtro ",
            df_selecionado.columns,
            default=[],
            key="showData_home"
        )

        if mostrarDados:
            st.write(df_selecionado[mostrarDados])

#Calculos estatisticos
    if not df_selecionado.empty:
        media_umidade = df_selecionado["umidade"].mean()
        media_temperatura = df_selecionado["temperatura"].mean()
        media_co2 = df_selecionado["co2"].mean()

        media1, media2, media3 = st.columns(3, gap="large")

        with media1:
            st.info("Média de Registros de Umidade")
            st.metric(label="Média", value=f"{media_umidade:.2f}")

        with media2:
            st.info("Média de Registros de Temperatura")
            st.metric(label="Média", value=f"{media_temperatura:.2f}")

        with media3:
            st.info("Média de Registros de CO2")
            st.metric(label="Média", value=f"{media_co2:.2f}")

        st.markdown("""--------""")

#GRAFICOS
def Graficos():
    st.title("Dashboard Monitoramento")

    aba1= st.info("Gráfico de Linhas")

    with aba1:
        if df_selecionado.empty:
            st.write("Nenhum dado está disponível para gerar o gráfico")
            return
        
        if colunaX == colunaY:
            st.warning("Selecione uma opção diferente para os eixos X e Y")
            return
        
        try:
            grupo_dados1 = df_selecionado.groupby(by=[colunaX]).size().reset_index(name="contagem")
            fig_valores = px.bar(
                grupo_dados1,
                x=colunaX,
                y="contagem",
                orientation="h",
                title=f"Contagem de Registros por {colunaX.capitalize()}",
                color_discrete_sequence=["#0083b8"],
                template="plotly_white"
            )

        except Exception as e:
            st.error(f"Erro ao criar o gráfico de linha: {e}")

        st.plotly_chart(fig_valores, use_container_width=True)

Home()
Graficos()