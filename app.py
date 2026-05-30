import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Bolão Copa 2026", page_icon="🏆", layout="wide")

st.title("🏆 Bolão Copa do Mundo 2026")
st.markdown("Dê seus palpites de placar e concorra ao grande prêmio!")

ARQUIVO_JOGOS = "palpites_jogos.csv"
ARQUIVO_RESULTADOS = "resultados_oficiais.csv"
ARQUIVO_EXTRAS = "resultados_extras.csv" # Novo arquivo para Campeão e Artilheiro oficiais

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
# CÁLCULO DO RANKING (ATUALIZADO COM CAMPEÃO E ARTILHEIRO)
# -----------------------------------------------------------------
def calcular_ranking():
    colunas_palpites = ["Nome", "Jogo ID", "Placar 1", "Placar 2", "Gols Apostados", "Campeao Apostado", "Artilheiro Apostado"]
    df_palpites = carregar_csv(ARQUIVO_JOGOS, colunas_palpites)
    df_resultados = carregar_csv(ARQUIVO_RESULTADOS, ["Jogo ID", "Placar 1 Real", "Placar 2 Real", "Gols Reais"])
    df_extras = carregar_csv(ARQUIVO_EXTRAS, ["Campeao Real", "Artilheiro Real"])
    
    if df_palpites.empty:
        return pd.DataFrame(columns=["Posição", "Nome", "Pontos Totais"])
        
    pontuacao = {}
    
    # Inicializa a pontuação de todo mundo que jogou
    for nome_usuario in df_palpites["Nome"].unique():
        pontuacao[nome_usuario] = 0

    # 1. Pontuação por Jogos
    if not df_resultados.empty:
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
                
                # Sistema de pontuação do placar
                if p1_a == p1_r and p2_a == p2_r:
                    pontuacao[nome] += 3
                else:
                    resultado_real = "M" if p1_r > p2_r else ("V" if p2_r > p1_r else "E")
                    resultado_apostado = "M" if p1_a > p2_a else ("V" if p2_a > p1_a else "E")
                    if resultado_real == resultado_apostado:
                        pontuacao[nome] += 1
                
                # Bônus de marcadores de gol
                if gols_apostados and gols_reais:
                    acertos_gols = 0
                    erros_gols = 0
                    for jogador in gols_apostados:
                        if jogador in gols_reais:
                            acertos_gols += gols_reais.count(jogador)
                        else:
                            erros_gols += 1
                    pontos_gols = max(0, acertos_gols - erros_gols)
                    pontuacao[nome] += pontos_gols

    # 2. Pontuação dos Extras (Campeão e Artilheiro de longo prazo)
    if not df_extras.empty:
        camp_real = str(df_extras.iloc[0]["Campeao Real"]).strip().lower()
        art_real = str(df_extras.iloc[0]["Artilheiro Real"]).strip().lower()
        
        # Pega o primeiro registro de palpite de cada usuário para checar as apostas master dele
        for nome in pontuacao.keys():
            user_palpites = df_palpites[df_palpites["Nome"] == nome]
            if not user_palpites.empty:
                # Compara Campeão (+5 pts)
                camp_ap = str(user_palpites.iloc[0].get("Campeao Apostado", "")).strip().lower()
                if camp_real and camp_ap == camp_real:
                    pontuacao[nome] += 5
                
                # Compara Artilheiro (+5 pts)
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
        🏃‍♂️ **Bônus de Marcadores de Gol (Opcional):**
        * **:red[🚨 Não é obrigatório escolher um marcador. É apenas um bônus!]**
        * **+1 ponto** por gol acertado na rodada.
        * ⚠️ **Regra Anti-Abuso:** Cada jogador escalado no seu palpite que passar em branco **ANULA** um acerto de gol.
        
        🏆 **Apostas Master de Longo Prazo:**
        * 🥇 **Acertou o Campeão da Copa:** **+5 pontos**
        * 👟 **Acertou o Artilheiro do Torneio:** **+5 pontos**
        """)
    
    st.write("---")
    st.header("Faça suas Apostas")
    
    nome = st.text_input("Seu Nome Completo:", key="nome_usuario")
    
    if nome.strip() != "":
        # Campos novos de longo prazo colocados em destaque logo no início do formulário
        st.subheader("🔮 Apostas Master da Copa (Preencha uma vez)")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            camp_aposta = st.text_input("Quem será o Grande Campeão da Copa 2026?", placeholder="Ex: Brasil", key="camp_aposta")
        with col_m2:
            art_aposta = st.text_input("Quem será o Artilheiro do Campeonato?", placeholder="Ex: Vini Jr", key="art_aposta")
            
        st.write("---")
        fase = st.selectbox("Escolha a Rodada:", ["Rodada 1"])
        st.info("💡 Digite os nomes dos jogadores que farão gols separados por vírgula (Ex: Neymar, Vini Jr). Se preferir não usar o bônus, deixe em branco.")
        
        palpites_form = {}
        
        for jogo in [j for j in JOGOS_COPA if j["fase"] == fase]:
            st.markdown(f"### {jogo['time1']} x {jogo['time2']} ({jogo['data']})")
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 3])
            with c1: st.write(f"**{jogo['time1']}**")
            with c2: p1 = st.number_input("Placar", min_value=0, max_value=15, step=1, key=f"p1_{jogo['id']}")
            with c3: st.write("X")
            with c4: p2 = st.number_input("Placar", min_value=0, max_value=15, step=1, key=f"p2_{jogo['id']}")
            with c5: st.write(f"**{jogo['time2']}**")
            
            gols = st.text_input(f"Quem fará os gols de {jogo['time1']} x {jogo['time2']}? (Opcional)", placeholder="Ex: Neymar, Vini Jr", key=f"gols_{jogo['id']}")
            
            palpites_form[jogo['id']] = {"t1": jogo['time1'], "t2": jogo['time2'], "p1": p1, "p2": p2, "gols": gols}
            st.write("---")
            
        if st.button("🚀 Salvar Meus Palpites"):
            df_atual = carregar_csv(ARQUIVO_JOGOS, ["Data Hora", "Nome", "Jogo ID", "Confronto", "Placar 1", "Placar 2", "Gols Apostados", "Campeao Apostado", "Artilheiro Apostado"])
            novas_linhas = []
            
            for j_id, dados in palpites_form.items():
                novas_linhas.append({
                    "Data Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "Nome": nome.strip(),
                    "Jogo ID": j_id,
                    "Confronto": f"{dados['t1']} x {dados['t2']}",
                    "Placar 1": int(dados["p1"]),
                    "Placar 2": int(dados["p2"]),
                    "Gols Apostados": dados["gols"].strip(),
                    "Campeao Apostado": camp_aposta.strip(),
                    "Artilheiro Apostado": art_aposta.strip()
                })
            df_final = pd.concat([df_atual, pd.DataFrame(novas_linhas)], ignore_index=True)
            df_final.to_csv(ARQUIVO_JOGOS, index=False)
            st.success("🎉 Seus palpites e apostas master foram registrados com sucesso!")
    else:
        st.warning("Insira seu nome completo para liberar os campos de apostas.")

# --- ABA 2: RANKING ---
with aba2:
    st.header("📊 Classificação Geral do Bolão")
    df_ranking_atual = calcular_ranking()
    if df_ranking_atual.empty:
        st.info("O ranking aparecerá aqui assim que o administrador lançar os primeiros resultados oficiais!")
    else:
        st.dataframe(df_ranking_atual, use_container_width=True, hide_index=True)

# --- ABA 3: ADMINISTRAÇÃO ---
with aba3:
    st.header("⚙️ Painel do Organizador")
    senha = st.text_input("Senha do Admin:", type="password")
    
    if senha == "1234":
        # Parte 1: Resultados dos Jogos Normais
        st.subheader("1. Inserir Resultado Oficial do Jogo")
        jogo_sel = st.selectbox("Selecione o Jogo Finalizado:", JOGOS_COPA, format_func=lambda x: f"{x['time1']} x {x['time2']}")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1: res_p1 = st.number_input(f"Placar Real {jogo_sel['time1']}", min_value=0, step=1)
        with col_r2: res_p2 = st.number_input(f"Placar Real {jogo_sel['time2']}", min_value=0, step=1)
            
        gols_reais_input = st.text_input("Quem marcou os gols? (Separados por vírgula)", placeholder="Ex: Neymar, Vini Jr")
        
        if st.button("💾 Publicar Resultado do Jogo"):
            df_res_atual = carregar_csv(ARQUIVO_RESULTADOS, ["Jogo ID", "Placar 1 Real", "Placar 2 Real", "Gols Reais"])
            df_res_atual = df_res_atual[df_res_atual["Jogo ID"] != jogo_sel["id"]]
            
            nova_linha_res = {
                "Jogo ID": jogo_sel["id"],
                "Placar 1 Real": int(res_p1),
                "Placar 2 Real": int(res_p2),
                "Gols Reais": gols_reais_input.strip()
            }
            df_res_final = pd.concat([df_res_atual, pd.DataFrame([nova_linha_res])], ignore_index=True)
            df_res_final.to_csv(ARQUIVO_RESULTADOS, index=False)
            st.success("⚽ Resultado do jogo publicado!")

        st.write("---")
        
        # Parte 2: Lançamento Final do Campeão e Artilheiro
        st.subheader("2. Definir Encerramento da Copa (Campeão & Artilheiro Real)")
        st.info("Deixe em branco até o final do campeonato. Quando preenchido, o sistema somará os 5 pontos extras automaticamente no ranking.")
        
        df_ex_atual = carregar_csv(ARQUIVO_EXTRAS, ["Campeao Real", "Artilheiro Real"])
        val_camp_inicial = df_ex_atual.iloc[0]["Campeao Real"] if not df_ex_atual.empty else ""
        val_art_inicial = df_ex_atual.iloc[0]["Artilheiro Real"] if not df_ex_atual.empty else ""
        
        col_adm1, col_adm2 = st.columns(2)
        with col_adm1:
            camp_oficial = st.text_input("Campeão Oficial da Copa:", value=val_camp_inicial)
        with col_adm2:
            art_oficial = st.text_input("Artilheiro Oficial da Copa:", value=val_art_inicial)
            
        if st.button("🏆 Publicar Encerramento da Copa"):
            df_novo_extra = pd.DataFrame([{
                "Campeao Real": camp_oficial.strip(),
                "Artilheiro Real": art_oficial.strip()
            }])
            df_novo_extra.to_csv(ARQUIVO_EXTRAS, index=False)
            st.success("🎉 Ganhadores oficiais da Copa publicados! Pontos extras adicionados ao ranking.")