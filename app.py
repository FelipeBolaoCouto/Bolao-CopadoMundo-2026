import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Bolão Copa 2026", page_icon="🏆", layout="wide")

st.title("🏆 Bolão Copa do Mundo 2026")
st.markdown("Dê seus palpites de placar e marcadores dos gols para subir no Ranking!")

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
# CÁLCULO DO RANKING (A MÁGICA DOS PONTOS)
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
                
            # 1. Regra de Vitória / Empate / Derrota
            resultado_real = "M" if p1_r > p2_r else ("V" if p2_r > p1_r else "E")
            resultado_apostado = "M" if p1_a > p2_a else ("V" if p2_a > p1_a else "E")
            
            if resultado_real == resultado_apostado:
                if resultado_real == "E":
                    pontuacao[nome] += 1
                else:
                    pontuacao[nome] += 3
            
            # 2. Regra dos Marcadores de Gols (Com anulamento)
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
    # PAINEL DE REGRAS E VALOR (ADICIONADO AQUI)
    st.markdown("""
    <div style="background-color: #1e293b; padding: 20px; border-radius: 10px; border-left: 5px solid #eab308; margin-bottom: 25px;">
        <h4 style="color: #eab308; margin-top: 0;">📜 Regulamento & Informações do Bolão</h4>
        <p style="font-size: 16px; margin-bottom: 8px;">💰 <b>Valor da Inscrição:</b> R$ 100,00 por participante.</p>
        <p style="font-size: 15px; margin-bottom: 5px;">⚽ <b>Sistema de Pontuação:</b></p>
        <ul style="font-size: 14px; margin-top: 5px;">
            <li><b>Acertou o vencedor</b> (ou acertou que haverá empate): <b>+3 pontos</b></li>
            <li><b>Acertou o empate</b> (placar igual, ex: 1x1): <b>+1 ponto</b></li>
            <li><b>Errou o resultado:</b> <b>0 pontos</b></li>
            <li><b>Marcadores de Gol:</b> <b>+1 ponto</b> por gol acertado.</li>
        </ul>
        <p style="font-size: 13px; color: #94a3b8; margin-bottom: 0;">
            ⚠️ <b>Anti-Abuso nos Marcadores:</b> Cada jogador escalado que passar em branco (não fizer gol) 
            <b>ANULA</b> um acerto de gol seu. Evite colocar o time inteiro!
        </p>
    </div>
    """, unsafe_html=True)

    st.header("Faça suas Apostas")
    fase = st.selectbox("Escolha a Rodada:", ["Rodada 1"])
    nome = st.text_input("Seu Nome Completo:", key="nome_usuario")
    
    if nome.strip() != "":
        st.info("💡 Digite os nomes dos jogadores que farão gols separados por vírgula (Ex: Neymar, Vini Jr). Se ninguém fizer gol, deixe em branco.")
        palpites_form = {}
        
        for jogo in [j for j in JOGOS_COPA if j["fase"] == fase]:
            st.markdown(f"### {jogo['time1']} x {jogo['time2']} ({jogo['data']})")
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 3])
            with c1: st.write(f"**{jogo['time1']}**")
            with c2: p1 = st.number_input("Placar", min_value=0, max_value=15, step=1, key=f"p1_{jogo['id']}")
            with c3: st.write("X")
            with c4: p2 = st.number_input("Placar", min_value=0, max_value=15, step=1, key=f"p2_{jogo['id']}")
            with c5: st.write(f"**{jogo['time2']}**")
            
            gols = st.text_input(f"Quem fará os gols de {jogo['time1']} x {jogo['time2']}?", placeholder="Ex: Neymar, Vini Jr", key=f"gols_{jogo['id']}")
            
            palpites_form[jogo['id']] = {"t1": jogo['time1'], "t2": jogo['time2'], "p1": p1, "p2": p2, "gols": gols}
            st.write("---")
            
        if st.button("🚀 Salvar Meus Palpites"):
            df_atual = carregar_csv(ARQUIVO_JOGOS, ["Data Hora", "Nome", "Jogo ID", "Confronto", "Placar 1", "Placar 2", "Gols Apostados"])
            novas_linhas = []
            
            for j_id, dados in palpites_form.items():
                novas_linhas.append({
                    "Data Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "Nome": nome.strip(),
                    "Jogo ID": j_id,
                    "Confronto": f"{dados['t1']} x {dados['t2']}",
                    "Placar 1": int(dados["p1"]),
                    "Placar 2": int(dados["p2"]),
                    "Gols Apostados": dados["gols"].strip()
                })
            df_final = pd.concat([df_atual, pd.DataFrame(novas_linhas)], ignore_index=True)
            df_final.to_csv(ARQUIVO_JOGOS, index=False)
            st.success("🎉 Seus palpites foram registrados!")
    else:
        st.warning("Insira seu nome completo para liberar os campos de apostas.")

# --- ABA 2: RANKING ---
with aba2:
    st.header("📊 Classification Geral do Bolão")
    df_ranking_atual = calcular_ranking()
    if df_ranking_atual.empty:
        st.info("O ranking aparecerá aqui assim que o administrador lançar os primeiros resultados oficiais!")
    else:
        st.dataframe(df_ranking_atual, use_container_width=True, hide_index=True)

# --- ABA 3: ADMINISTRAÇÃO ---
with aba3:
    st.header("⚙️ Painel do Organizador")
    senha = st.text_input("Senha do Administrador:", type="password")
    
    if senha == "1234":
        st.subheader("Inserir Resultado Oficial do Jogo")
        jogo_sel = st.selectbox("Selecione o Jogo Finalizado:", JOGOS_COPA, format_func=lambda x: f"{x['time1']} x {x['time2']}")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1: res_p1 = st.number_input(f"Placar Real {jogo_sel['time1']}", min_value=0, step=1)
        with col_r2: res_p2 = st.number_input(f"Placar Real {jogo_sel['time2']}", min_value=0, step=1)
            
        gols_reais_input = st.text_input("Quem marcou os gols na realidade? (Separados por vírgula)", placeholder="Ex: Neymar, Neymar, Marroquino")
        
        if st.button("💾 Publicar Resultado Oficial"):
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
            st.success("⚽ Resultado e marcadores publicados! O ranking foi recalculado.")