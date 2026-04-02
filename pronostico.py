import streamlit as st
import math

def poisson(mu, k):
    return (math.exp(-mu) * (mu**k)) / math.factorial(k)

st.title("⚽ Elite Betting Analyzer")
st.write("Inserisci i dati per ottenere il pronostico matematico.")

# Sidebar per i nomi
with st.sidebar:
    st.header("Configurazione Match")
    casa = st.text_input("Squadra Casa", "Inter")
    ospite = st.text_input("Squadra Ospite", "Milan")

# Layout a colonne per i dati
col1, col2 = st.columns(2)

with col1:
    st.subheader(casa)
    gf_c = st.number_input(f"Gf Casa ({casa})", value=1.5)
    gs_c = st.number_input(f"Gs Casa ({casa})", value=1.0)
    tiri_c = st.number_input(f"Tiri in Porta ({casa})", value=4.5)
    poss_c = st.slider(f"% Possesso ({casa})", 0, 100, 50)

with col2:
    st.subheader(ospite)
    gf_o = st.number_input(f"Gf Fuori ({ospite})", value=1.2)
    gs_o = st.number_input(f"Gs Fuori ({ospite})", value=1.3)
    tiri_o = st.number_input(f"Tiri in Porta ({ospite})", value=3.8)

if st.button("ANALIZZA PARTITA"):
    # Logica Matematica (la stessa di prima)
    mu_casa = ((gf_c + gs_o) / 2) * (tiri_c / 4) * (poss_c / 50)
    mu_ospite = ((gf_o + gs_c) / 2) * (tiri_o / 4) * ((100 - poss_c) / 50)
    
    p1, px, p2 = 0, 0, 0
    p_under = 0
    for gc in range(8):
        for go in range(8):
            prob = poisson(mu_casa, gc) * poisson(mu_ospite, go)
            if gc > go: p1 += prob
            elif gc == go: px += prob
            else: p2 += prob
            if (gc + go) < 2.5: p_under += prob

    # Visualizzazione risultati professionale
    st.divider()
    st.success(f"Analisi Completata: {casa} vs {ospite}")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Vittoria 1", f"{p1:.1%}")
    c2.metric("Pareggio X", f"{px:.1%}")
    c3.metric("Vittoria 2", f"{p2:.1%}")
    
    st.info(f"Probabilità Over 2.5: {1-p_under:.1%}")

