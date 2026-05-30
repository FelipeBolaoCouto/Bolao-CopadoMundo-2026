import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Bolão Copa 2026", page_icon="🏆", layout="centered")

st.title("🏆 Bolão Copa do Mundo 2026")
st.markdown("Dê os seus palpites de placar para cada rodada e suba no ranking!")

ARQUIVO_JOGOS = "palpites_jogos.csv"

# Banco de dados simulado dos primeiros grandes jogos da Fase de Grupos (Copa 2026)
# Você pode expandir ou mudar essa lista com os jogos que preferir!
JOGOS_COPA = [
    {"id": 1, "fase": "Rodada 1", "data": "11/06", "time1": "México", "time2": "África do Sul"},
    {"id": 2, "fase": "Rodada 1", "data": "12/06", "time1": "EUA", "time2": "Paraguai"},
    {"id": 3, "fase": "Rodada 1", "data": "12/06", "time1": "Canadá", "time2": "Bósnia"},
    {"id": 4, "fase": "Rodada 1", "data": "13/06", "time1": "Brasil", "time2": "Marrocos"},
    {"id": 5, "fase": "Rodada 1", "data": "14/06", "time1": "Alemanha", "time2": "Curaçao"},
    {"id": 6, "fase": "Rodada 1", "data": "14/06", "time1": "Holanda", "time2": "Japão"},
    
    {"id": 7, "fase": "Rodada 2", "data": "18/06", "time1": "México", "time2": "Coreia do Sul"},
    {"id": 8, "fase": "Rodada 2", "data": "19/06", "time1": "EUA", "time2": "Austrália"},
    {"id": 9, "fase": "Rodada 2", "data": "19/06", "time1": "Brasil", "time2": "Haiti"},
    {"id": 10, "fase": "Rodada 2", "data": "20/06", "time1": "Alemanha", "time2": "Costa do Marfim"},
]

# Função para carregar os palpites já salvos
def carregar_palpites():
    if os.path.exists(ARQUIVO_JOGOS):
        try:
            return pd.read_csv(ARQUIVO_JOGOS)
        except:
            return pd.DataFrame(columns=["Data Hora", "Nome", "Jogo ID", "Confronto", "Placar 1", "Placar 2"])
    else:
        return pd.DataFrame(columns=["Data Hora", "Nome", "Jogo ID", "Confronto", "Placar 1", "Placar 2"])

# -----------------------------------------------------------------
# SELEÇÃO DA RODADA / FILTRO
# -----------------------------------------------------------------
st.sidebar.header("Navegação")
fase_selecionada = st.sidebar.selectbox("Escolha a Fase/Rodada:", ["Rodada 1", "Rodada 2"])

# Filtrando os jogos com base na escolha do usuário
jogos_filtrados = [j for j in JOGOS_COPA if j["fase"] == fase_selecionada]

# -----------------------------------------------------------------
# FORMULÁRIO DE PALPITES
# -----------------------------------------------------------------
st.header(f"📝 Enviar Palpites - {fase_selecionada}")

nome = st.text_input("Qual é o seu nome completo?", placeholder="Digite seu nome para salvar")

# Dicionário temporário para guardar os inputs do formulário de forma dinâmica
palpites_formulario = {}

if nome.strip() != "":
    st.markdown("### Insira os placares abaixo:")
    
    # Gerando os campos de palpite dinamicamente para cada jogo filtrado
    for jogo in jogos_filtrados:
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
        
        with col1:
            st.write(f"**{jogo['time1']}**")
        with col2:
            placar1 = st.number_input("", min_value=0, max_value=15, step=1, key=f"t1_{jogo['id']}", value=0)
        with col3:
            st.write("X")
        with col4:
            placar2 = st.number_input("", min_value=0, max_value=15, step=1, key=f"t2_{jogo['id']}", value=0)
        with col5:
            st.write(f"**{jogo['time2']}** ({jogo['data']})")
            
        # Guarda o valor digitado associando ao ID do jogo
        palpites_formulario[jogo['id']] = {
            "confronto": f"{jogo['time1']} x {jogo['time2']}",
            "p1": placar1,
            "p2": placar2
        }
        st.write("---")
        
    botao_salvar = st.button("🚀 Salvar Meus Palpites desta Rodada")
    
    if botao_salvar:
        df_atual = carregar_palpites()
        novas_linhas = []
        
        # Estrutura os dados para salvar linha por linha no CSV
        for jogo_id, dados in palpites_formulario.items():
            nova_linha = {
                "Data Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "Nome": nome.strip(),
                "Jogo ID": jogo_id,
                "Confronto": dados["confronto"],
                "Placar 1": int(dados["p1"]),
                "Placar 2": int(dados["p2"])
            }
            novas_linhas.append(nova_linha)
            
        df_novos_palpites = pd.DataFrame(novas_linhas)
        df_final = pd.concat([df_atual, df_novos_palpites], ignore_index=True)
        df_final.to_csv(ARQUIVO_JOGOS, index=False)
        
        st.success(f"🎉 Pronto, {nome}! Seus palpites da **{fase_selecionada}** foram computados com sucesso!")
else:
    st.info("💡 Por favor, insira o seu nome completo acima para liberar os campos de apostas.")

# -----------------------------------------------------------------
# VER TODOS OS PALPITES DA GALERA
# -----------------------------------------------------------------
st.write("###")
st.header("📊 Histórico Geral de Apostas")

df_exibir = carregar_palpites()

if df_exibir.empty:
    st.info("Nenhum palpite enviado ainda. Comece a apostar! ⚽")
else:
    st.dataframe(df_exibir[["Nome", "Confronto", "Placar 1", "Placar 2", "Data Hora"]], use_container_width=True, hide_index=True)