import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Bolão Copa 2026", page_icon="🏆", layout="centered")

st.title("🏆 Bolão Copa do Mundo 2026")
st.markdown("Insira o seu nome e dê os seus palpites para entrar no ranking oficial!")

# Nome do arquivo onde os dados serão salvos dentro do servidor do Streamlit
ARQUIVO_DADOS = "palpites.csv"

# Função para carregar os dados existentes
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            return pd.read_csv(ARQUIVO_DADOS)
        except:
            return pd.DataFrame(columns=["Data Hora", "Nome", "Palpite Campeao", "Palpite Vice"])
    else:
        return pd.DataFrame(columns=["Data Hora", "Nome", "Palpite Campeao", "Palpite Vice"])

# -----------------------------------------------------------------
# FORMULÁRIO DE INSCRIÇÃO / PALPITES
# -----------------------------------------------------------------
st.header("📝 Enviar Novo Palpite")

with st.form(key="form_palpite", clear_on_submit=True):
    nome = st.text_input("Qual é o seu nome completo?")
    campeao = st.text_input("Quem será o Campeão do Mundo?")
    vice = st.text_input("Quem será o Vice-Campeão?")
    
    botao_enviar = st.form_submit_button(label="🚀 Confirmar Palpite")

if botao_enviar:
    if nome.strip() == "" or campeao.strip() == "" or vice.strip() == "":
        st.error("⚠️ Por favor, preencha todos os campos antes de enviar!")
    else:
        # 1. Carrega o histórico
        df_atual = carregar_dados()
        
        # 2. Cria a nova linha
        nova_linha = {
            "Data Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Nome": nome.strip(),
            "Palpite Campeao": campeao.strip(),
            "Palpite Vice": vice.strip()
        }
        
        # 3. Adiciona e salva no arquivo
        df_novo = pd.concat([df_atual, pd.DataFrame([nova_linha])], ignore_index=True)
        df_novo.to_csv(ARQUIVO_DADOS, index=False)
        
        st.success(f"🎉 Maravilha, {nome}! O seu palpite foi registrado com sucesso! Atualize a página se necessário.")

# -----------------------------------------------------------------
# VISUALIZAÇÃO DOS PARTICIPANTES (RANKING / LISTA)
# -----------------------------------------------------------------
st.write("---")
st.header("📊 Participantes Confirmados")

df_exibir = carregar_dados()

if df_exibir.empty or len(df_exibir) == 0:
    st.info("Ainda não temos participantes cadastrados. Seja o primeiro! ⚽")
else:
    # Remove linhas em branco por segurança
    df_exibir = df_exibir.dropna(subset=["Nome"])
    
    # Exibe a tabela na tela
    st.dataframe(
        df_exibir[["Nome", "Palpite Campeao", "Palpite Vice"]], 
        use_container_width=True,
        hide_index=True
    )