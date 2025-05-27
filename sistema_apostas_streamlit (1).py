
import streamlit as st
import pandas as pd
import requests
import random
from datetime import datetime, timedelta
from sklearn.linear_model import LogisticRegression
import numpy as np

# Modelo IA simples
model = LogisticRegression().fit(np.array([[1.35], [2.2], [1.85], [3.1]]), np.array([0, 2, 0, 1]))
inv_resultado_map = {0: "Vitória Casa", 1: "Empate", 2: "Vitória Fora"}

def sugestao_ia(odd):
    prob = model.predict_proba([[odd]])[0]
    pred = np.argmax(prob)
    return f"{inv_resultado_map[pred]} ({prob[pred]*100:.0f}%)", prob[pred]*100

def carregar_jogos(api_key):
    jogos = []
    headers = {"x-apisports-key": api_key}
    hoje = datetime.today()
    try:
        for dias in range(3):
            data_str = (hoje + timedelta(days=dias)).strftime("%Y-%m-%d")
            url = f"https://v3.football.api-sports.io/fixtures?date={data_str}"
            r = requests.get(url, headers=headers, timeout=10)
            data = r.json()
            for item in data["response"]:
                home = item["teams"]["home"]["name"]
                away = item["teams"]["away"]["name"]
                dt = datetime.strptime(item['fixture']['date'], "%Y-%m-%dT%H:%M:%S%z")
                status = item["fixture"]["status"]["short"]
                placar = "-"
                if item["goals"]["home"] is not None:
                    placar = f"{item['goals']['home']}x{item['goals']['away']}"
                jogos.append({
                    "DataHora": dt.strftime("%d/%m - %H:%M"),
                    "Jogo": f"{home} x {away}",
                    "Odd": round(random.uniform(1.3, 3.5), 2),
                    "Status": "Finalizado" if status == "FT" else "Em Andamento",
                    "Placar": placar
                })
    except Exception as e:
        st.error(f"Erro ao carregar dados da API: {e}")
    return jogos

def aplicar_analise(jogos):
    resultados = []
    for j in jogos:
        palpite, conf_ia = sugestao_ia(j["Odd"])
        odd = j["Odd"]
        if conf_ia >= 65 and odd < 1.8:
            cor = "#cce5ff"  # Azul
        elif conf_ia >= 60 and 1.75 <= odd <= 2.7:
            cor = "#d4edda"  # Verde
        elif 50 <= conf_ia < 60:
            cor = "#fff3cd"  # Amarelo
        else:
            cor = "#f8d7da"  # Vermelho
        resultados.append({**j, "IA": palpite, "Confiança": conf_ia, "Cor": cor})
    return resultados

st.set_page_config(page_title="Sistema Apostas IA", layout="wide")
st.title("🔮 Sistema de Apostas com IA")

api_key = st.text_input("Insere tua API Key da API-SPORTS:", type="password")

if api_key:
    jogos = carregar_jogos(api_key)
    if jogos:
        analisados = aplicar_analise(jogos)
        df = pd.DataFrame(analisados)
        df_display = df[["DataHora", "Jogo", "Odd", "Status", "Placar", "IA"]]

        def colorir_linha(row):
            return [f"background-color: {row['Cor']}" for _ in row]

        st.dataframe(df_display.style.apply(colorir_linha, axis=1))
    else:
        st.warning("Nenhum jogo encontrado.")
else:
    st.info("Por favor, insere a tua chave de API para começar.")
