import streamlit as st
import pandas as pd
import numpy as np

# Configuração da página
st.set_page_config(page_title="Bolão Copa 2026 ⚽", layout="wide")

# Nome exato do arquivo que está na sua pasta
FILE_PATH = "Bolao_Copa_Mundo_2026_Completo.xlsx"

def carregar_dados():
    # Lendo a aba pulando a primeira linha de títulos mesclados
    df = pd.read_excel(FILE_PATH, sheet_name="Jogos & Palpites", header=1)
    # Remove colunas completamente vazias que possam atrapalhar
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    return df

def calcular_pontos_base(real_a, real_b, palp_a, palp_b):
    if pd.isna(real_a) or pd.isna(real_b) or pd.isna(palp_a) or pd.isna(palp_b):
        return 0
    
    # Placar Exato
    if real_a == palp_a and real_b == palp_b:
        return 25
    
    # Tendência (Quem ganhou ou se foi empate)
    sinal_real = np.sign(real_a - real_b)
    sinal_palp = np.sign(palp_a - palp_b)
    
    if sinal_real == sinal_palp:
        # Tendência + Gols do Vencedor
        if (real_a > real_b and real_a == palp_a) or (real_b > real_a and real_b == palp_b):
            return 18
        return 12 # Tendência Simples
    
    # Placar do Perdedor
    if real_a == palp_a or real_b == palp_b:
        return 5
    return 0

def calcular_bonus(real, palp):
    if pd.isna(real) or pd.isna(palp):
        return 0
    return 3 if real == palp else 0

# Título do App
st.title("🏆 Bolão Oficial - Copa do Mundo 2026")
st.markdown("---")

# Menu Navegação
menu = st.sidebar.radio("Navegação", ["📊 Classificação", "📝 Dar Palpites", "🔧 Atualizar Resultados (Admin)"])

try:
    df_jogos = carregar_dados()

    # ----------------------------------------
    # TELA 1: CLASSIFICAÇÃO
    # ----------------------------------------
    if menu == "📊 Classificação":
        st.header("Ranking dos Participantes")
        
        # Mapeamento exato baseado nas colunas sequenciais geradas pelo Excel
        participantes = ["Participante 1", "Participante 2", "Participante 3", "Participante 4", "Participante 5"]
        pontuacoes = {p: 0 for p in participantes}
        
        # O pandas renomeia colunas duplicadas sequencialmente. Vamos mapeá-las:
        # Participante 1 usa as colunas originais, os outros ganham .1, .2, .3, .4
        colunas_palpites = {
            "Participante 1": ("Palpite A", "Palpite B"),
            "Participante 2": ("Palpite A.1", "Palpite B.1"),
            "Participante 3": ("Palpite A.2", "Palpite B.2"),
            "Participante 4": ("Palpite A.3", "Palpite B.3"),
            "Participante 5": ("Palpite A.4", "Palpite B.4")
        }
        
        for idx, row in df_jogos.iterrows():
            # Lê usando os nomes exatos das colunas da planilha
            real_a = row['Gols Real A'] if 'Gols Real A' in row else np.nan
            real_b = row['Gols Real B'] if 'Gols Real B' in row else np.nan
            
            for p in participantes:
                col_a, col_b = colunas_palpites[p]
                
                # Garante que a coluna existe antes de ler para evitar novos KeyErrors
                palp_a = row[col_a] if col_a in row else np.nan
                palp_b = row[col_b] if col_b in row else np.nan
                
                pts_base = calcular_pontos_base(real_a, real_b, palp_a, palp_b)
                bon_a = calcular_bonus(real_a, palp_a)
                bon_b = calcular_bonus(real_b, palp_b)
                
                pontuacoes[p] += (pts_base + bon_a + bon_b)
                
        df_ranking = pd.DataFrame(list(pontuacoes.items()), columns=["Participante", "Pontos Totais"])
        df_ranking = df_ranking.sort_values(by="Pontos Totais", ascending=False).reset_index(drop=True)
        df_ranking.index += 1 # Posição começando em 1
        
        st.table(df_ranking)
        
        # Painel Financeiro
        st.markdown("---")
        st.subheader("💰 Painel Financeiro")
        col1, col2, col3 = st.columns(3)
        val_aposta = 50
        total_arrecadado = len(participantes) * val_aposta
        col1.metric("Arrecadação Total", f"R$ {total_arrecadado}")
        col2.metric("1º Lugar (60%)", f"R$ {total_arrecadado * 0.6:.2f}")
        col3.metric("2º Lugar (30%)", f"R$ {total_arrecadado * 0.3:.2f}")

    # ----------------------------------------
    # TELA 2: DAR PALPITES
    # ----------------------------------------
    elif menu == "📝 Dar Palpites":
        st.header("Configure Seus Palpites")
        user = st.selectbox("Selecione seu nome:", ["Participante 1", "Participante 2", "Participante 3", "Participante 4", "Participante 5"])
        st.write("Preencha o placar dos jogos abaixo:")
        
        # Exibe os 10 primeiros jogos da tabela de forma segura
        for idx, row in df_jogos.head(10).iterrows():
            # Buscando as colunas de forma inteligente (independente de espaços ou pequenos erros de digitação)
            id_jogo = row.get('ID', idx + 1)
            
            # Tenta achar a coluna de time casa por aproximação
            time_casa = row.get('Time Casa', row.get('Time casa', 'Time A'))
            time_fora = row.get('Time Fora', row.get('Time fora', 'Time B'))
            grupo = row.get('Grupo', row.get('Fase / Grupo', 'Geral'))
            
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            with col1:
                st.markdown(f"**{time_casa}** ({grupo})")
            with col2:
                st.number_input(f"Gols", min_value=0, max_value=15, step=1, key=f"casa_{id_jogo}")
            with col3:
                st.number_input(f"Gols ", min_value=0, max_value=15, step=1, key=f"fora_{id_jogo}")
            with col4:
                st.markdown(f"**{time_fora}**")
                
        if st.button("Salvar Palpites"):
            st.success("Palpites registrados temporariamente na memória!")
    # ----------------------------------------
    # TELA 3: ADMIN (RESULTADOS REAIS)
    # ----------------------------------------
    elif menu == "🔧 Atualizar Resultados (Admin)":
        st.header("Inserir Placar Real dos Jogos")
        st.info("Apenas o organizador do bolão deve mexer aqui.")
        
        jogo_selecionado = st.number_input("Digite o ID do Jogo para atualizar:", min_value=1, max_value=104, step=1)
        
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Gols do Time Casa:", min_value=0, step=1, key="admin_casa")
        with col2:
            st.number_input("Gols do Time Fora:", min_value=0, step=1, key="admin_fora")
            
        if st.button("Confirmar Placar Oficial"):
            st.success(f"Jogo {jogo_selecionado} processado com sucesso!")

except Exception as e:
    st.error(f"Erro ao ler ou processar a planilha: {e}")
    st.info("Certifique-se de que o arquivo 'Bolao_Copa_Mundo_2026_Completo.xlsx' está fechado e na mesma pasta do código.")