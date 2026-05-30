import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Bolão Copa 2026", page_icon="🏆", layout="wide")

st.title("🏆 Bolão Copa do Mundo 2026")
st.markdown("Dê seus palpites de placar e concorra ao grande prêmio!")

ARQUIVO_JOGOS = "palpites_jogos.csv"
ARQUIVO_RESULTADOS = "resultados_oficiais.csv"
ARQUIVO_EXTRAS = "resultados_extras.csv"

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
# CÁLCULO DO RANKING (SEM MARCADORES DE GOLS)
# -----------------------------------------------------------------
def calcular_ranking():
    colunas_palpites = ["Nome", "Jogo ID", "Placar 1", "Placar 2", "Campeao Apostado", "Artilheiro Apostado"]
    df_palpites = carregar_csv(ARQUIVO_JOGOS, colunas_palpites)
    df_resultados = carregar_csv(ARQUIVO_RESULTADOS, ["Jogo ID", "Placar 1 Real", "Placar 2 Real"])
    df_extras = carregar_csv(ARQUIVO_EXTRAS, ["Campeao Real", "Artilheiro Real"])
    
    if df_palpites.empty:
        return pd.DataFrame(columns=["Posição", "Nome", "Pontos Totais"])
        
    pontuacao = {}
    
    # Inicializa a pontuação de todos os participantes ativos
    for nome_usuario in df_palpites["Nome"].unique():
        pontuacao[nome_usuario] = 0

    # 1. Pontuação Base dos Jogos
    if not df_resultados.empty:
        for _, res in df_resultados.iterrows():
            j_id = int(res["Jogo ID"])
            p1_r = int(res["Placar 1 Real"])
            p2_r = int(res["Placar 2 Real"])
            
            palpites_jogo = df_palpites[df_palpites["Jogo ID"] == j_id]
            
            for _, palpite in palpites_jogo.iterrows():
                nome = palpite["Nome"]
                p1_a = int(palpite["Placar 1"])
                p2_a = int(palpite["Placar 2"])
                
                # Sistema de pontuação focado no placar
                if p1_a == p1_r and p2_a == p2_r:
                    pontuacao[nome] += 3
                else:
                    resultado_real = "M" if p1_r > p2_r else ("V" if p2_r > p1_r else "E")
                    resultado_apostado = "M" if p1_a > p2_a else ("V" if p2_a > p1_a else "E")
                    if resultado_real == resultado_apostado:
                        pontuacao[nome] += 1

    # 2. Pontuação Master de Longo Prazo (Campeão e Artilheiro)
    if not df_extras.empty:
        camp_real = str(df_extras.iloc[0]["Campeao Real"]).strip().lower()
        art_real = str(df_extras.iloc[0]["Artilheiro Real"]).strip().lower()
        
        for nome in pontuacao.keys():
            user_palpites = df_palpites[df_palpites["Nome"] == nome]
            if not user_palpites.empty:
                # Acerto de Campeão (+5 pts)
                camp_ap = str(user_palpites.iloc[0].get("Campeao Apostado", "")).strip().lower()
                if camp_real and camp_ap == camp_real:
                    pontuacao[nome] += 5
                
                # Acerto de Artilheiro (+5 pts)
                art_ap = str(user_palpites.iloc[0].get("Artilheiro Apostado", "")).strip().lower()
                if art_real and art_ap == art_real:
                    pontuacao[nome] += 5

    df_rank = pd.DataFrame(list(pontuacao.items()), columns=["Nome", "Pontos Totais"])
    df_rank = df_rank.sort_values(by="Pontos Totais", ascending=False).reset_index(drop=True)
    df_rank.insert(0, "Posição", df_rank.index + 1)
    return df_rank

# -----------------------------------------------------------------
# CRIAÇÃO DAS ABAS NA TELA
# -----------------------------------------------------------------
aba1, aba2, aba3 = st.tabs(["📝 Dar Palpites", "📊 Ranking Geral", "⚙️ Área do Admin"])

# --- ABA 1: FORMULÁRIO DE PALPITES ---
with aba1:
    # REGULAMENTO ENXUTO (SEM MARCADORES DE GOL)
    st.warning("📜 **Regulamento & Informações Importantes do Bolão**")
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown("💰 **Valor da Inscrição:** R$ 100,00 por participante.")
        st.markdown("""
        ⚽ **Sistema de Pontuação dos Placares:**
        * 🔥 **Acertou o resultado exato** (vitória ou empate): **+3 pontos**
        * 🎯 **Acertou o resultado** (vitória ou empate, mas errou o placar exato): **+1 ponto**
        * ❌ **Errou o resultado completo**: **0 pontos**
        """)
    with col_info2:
        st.markdown("""
        🏆 **Apostas Master de Longo Prazo:**
        * 🥇 **Acertou o Campeão da Copa:** **+5 pontos