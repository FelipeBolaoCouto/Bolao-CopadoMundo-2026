import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Bolão Copa 2026", page_icon="🏆", layout="wide")

st.title("🏆 Bolão Copa do Mundo 2026")
st.markdown("Dê seus palpites de placar e concorra ao grande prêmio!")

ARQUIVO_JOGOS = "palpites_jogos.csv"
ARQUIVO_RESULTADOS = "resultados_oficiais.csv"

# Lista de jogos cadastrados
JOGOS_COPA = [
    {"id": 1, "fase": "Rodada 1", "data": "11/06", "time1": "México", "time2": "África do Sul"},
    {"id": 2, "fase": "Rodada 1", "data": "12/06", "time1": "EUA", "time2": "Paraguai"},
    {"id": 3, "fase": "Rodada 1", "data": "12/06", "time1": "Canadá", "time2": "Bósnia"},
    {"id": 4, "fase": "Rodada 1", "data": "13/06", "time1": "Brasil", "time2": "Marrocos"},
]

# Funções auxiliares de banco de dados
def carregar_csv(arquivo, colunas):
    if os.path.exists(arquivo):
        try: 
            return pd.read_csv(arquivo)
        except: 
            return pd.DataFrame(columns=colunas)
    return pd.DataFrame(columns=colunas)

# -----------------------------------------------------------------
# CÁLCULO DO RANKING (REGRAS UNIFICADAS)
# -----------------------------------------------------------------
def calcular_ranking():
    df_palpites = carregar_csv(ARQUIVO_JOGOS, ["Nome", "Jogo ID", "Placar 1", "Placar 2", "Gols Apostados"])
    df_resultados = carregar_csv(ARQUIVO_RESULTADOS, ["Jogo ID", "Placar 1 Real", "Placar 2 Real", "Gols Reais"])
    
    if df_palpites.empty or df_resultados.empty:
        return pd.DataFrame(columns=["Posição", "Nome", "Pontos Totais"])
        
    pontuacao = {}
    
    for _, res in df_resultados.iterrows():
        j_id = int(res["Jogo ID"])
        p1_r = int(res["Placar 1 Real"])
        p2_r = int(res["Placar 2 Real"])
        gols_reais = [g.strip().lower() for g in str(res["Gols Reais"]).split(",") if g.strip()]
        
        palpites_jogo = df_palpites[df_palpites["Jogo ID"] == j_id]
        
        for _, palpite in palpites_jogo.iterrows():
            nome = palpite["Nome"]
            p1_a = int(palpite["Placar 1"])
            p2_a = int(palpite["Placar 2"])
            gols_apostados = [g.strip().lower() for g in str(palpite["Gols Apostados"]).split(",") if g.strip()]
            
            if nome not in pontuacao:
                pontuacao[nome] = 0
                
            # --- SISTEMA DE PONTUAÇÃO DO PLACAR UNIFICADO ---
            if p1_a == p1_r and p2_a == p2_r:
                # Acertou o resultado exato (vitoria ou empate) -> 3 pontos
                pontuacao[nome] += 3
            else:
                # Verifica se acertou a tendência/resultado (vitoria ou empate) -> 1 ponto
                resultado_real = "M" if p1_r > p2_r else ("V" if p2_r > p1_r else "E")
                resultado_apostado = "M" if p1_a > p2_a else ("V" if p2_a > p1_a else "E")
                
                if resultado_real == resultado_apostado:
                    pontuacao[nome] += 1
            
            # 3. Regra dos Marcadores de Gols (Bônus Opcional com Anulamento)
            if gols_apostados and gols_reais:
                acertos_gols = 0
                erros_gols = 0
                
                for jogador in gols_apostados:
                    if jogador in gols_reais:
                        acertos_gols += gols_reais.count(jogador)
                    else:
                        erros_gols += 1
                
                pontos_gols = max(0, acertos_gols - erros_gols)
                pontuacao[nome] += pontos