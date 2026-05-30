import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Bolão Copa 2026", page_icon="🏆", layout="centered")

st.title("🏆 Bolão Copa do Mundo 2026")
st.markdown("Insira o seu nome e dê os seus palpites para entrar no ranking oficial!")

# URL da sua planilha do Google (com permissão de Editor)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1no9zRPwJxa1FiEyWh3oEIf2SD6DMp64-PNQG6H46bA8/edit?usp=sharing"

# Estabelecer conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

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
        try:
            # 1. Ler os dados existentes para não apagar o que já foi salvo
            dados_existentes = conn.read(spreadsheet=URL_PLANILHA, usecols=[0, 1, 2, 3])
            df_atual = pd.DataFrame(dados_existentes)
        except Exception:
            # Se a planilha estiver totalmente vazia e der erro na leitura, cria um DataFrame limpo
            df_atual = pd.DataFrame(columns=["Data Hora", "Nome", "Palpite Campeao", "Palpite Vice"])
        
        # 2. Criar a nova linha com o palpite atual
        nova_linha = {
            "Data Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Nome": nome.strip(),
            "Palpite Campeao": campeao.strip(),
            "Palpite Vice": vice.strip()
        }
        
        # 3. Juntar o novo palpite aos dados antigos
        df_novo = pd.concat([df_atual, pd.DataFrame([nova_linha])], ignore_index=True)
        
        # 4. Gravar de volta na planilha do Google
        conn.update(spreadsheet=URL_PLANILHA, data=df_novo)
        
        st.success(f"🎉 Maravilha, {nome}! O seu palpite foi registrado com sucesso!")

# -----------------------------------------------------------------
# VISUALIZAÇÃO DOS PARTICIPANTES (RANKING / LISTA)
# -----------------------------------------------------------------
st.write("---")
st.header("📊 Participantes Confirmados")

try:
    # Ler os dados atualizados para exibir na tela
    dados_finais = conn.read(spreadsheet=URL_PLANILHA)
    df_finais = pd.DataFrame(dados_finais)
    
    if df_finais.empty or len(df_finais) == 0:
        st.info("Ainda não temos participantes cadastrados. Seja o primeiro! ⚽")
    else:
        # Remover linhas totalmente vazias que o Google Sheets possa trazer por engano
        df_finais = df_finais.dropna(subset=["Nome"])
        
        # Exibir a tabela bonita para os usuários acompanharem os palpites uns dos outros
        st.dataframe(
            df_finais[["Nome", "Palpite Campeao", "Palpite Vice"]], 
            use_container_width=True,
            hide_index=True
        )
except Exception as e:
    st.info("Aguardando os primeiros cadastros para exibir o pódio! 🕒")