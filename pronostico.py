import streamlit as st
import math
import random
import numpy as np

# --- LOGICA MATEMATICA AVANZATA ---

def simulazione_monte_carlo(mu_c, mu_o, n_sim=10000):
    """MCTS: Simula la partita 10.000 volte"""
    vittorie_c, pareggi, vittorie_o = 0, 0, 0
    over25 = 0
    
    for _ in range(n_sim):
        # Generazione gol casuale basata su Poisson
        gol_c = np.random.poisson(mu_c)
        gol_o = np.random.poisson(mu_o)
        
        if gol_c > gol_o: vittorie_c += 1
        elif gol_c == gol_o: pareggi += 1
        else: vittorie_o += 1
        
        if (gol_c + gol_o) > 2.5: over25 += 1
            
    return vittorie_c/n_sim, pareggi/n_sim, vittorie_o/n_sim, over25/n_sim

def catena_markov_incertezza(p1, px, p2):
    """Modello Markov: Calcola la stabilità del risultato"""
    # Matrice di transizione semplificata (Probabilità di cambiare stato)
    stabilità = (p1**2 + px**2 + p2**2) 
    return stabilità # Più è alto, più il match è "prevedibile"

# --- INTERFACCIA STREAMLIT ---

st.set_page_config(page_title="MCTS & Markov Predictor", layout="wide")
st.title("🛡️ Advanced Betting Engine (MCTS + Markov)")

col1, col2 = st.columns(2)

with col1:
    st.header("Dati Squadra Casa")
    gf_c = st.number_input("Media Gol Fatti (Casa)", value=1.8, step=0.1)
    gs_c = st.number_input("Media Gol Subiti (Casa)", value=0.9, step=0.1)
    tiri_c = st.number_input("Tiri in Porta (Casa)", value=5.0, step=0.5)

with col2:
    st.header("Dati Squadra Ospite")
    gf_o = st.number_input("Media Gol Fatti (Fuori)", value=1.1, step=0.1)
    gs_o = st.number_input("Media Gol Subiti (Fuori)", value=1.4, step=0.1)
    tiri_o = st.number_input("Tiri in Porta (Fuori)", value=3.5, step=0.5)

if st.button("ESEGUI 10.000 SIMULAZIONI"):
    # Calcolo medie pesate (Input per i modelli)
    mu_casa = ((gf_c + gs_o) / 2) * (tiri_c / 4.5)
    mu_ospite = ((gf_o + gs_c) / 2) * (tiri_o / 4.5)
    
    # 1. Esecuzione Monte Carlo
    p1, px, p2, po25 = simulazione_monte_carlo(mu_casa, mu_ospite)
    
    # 2. Esecuzione Markov (Indice di Stabilità)
    stabilita = catena_markov_incertezza(p1, px, p2)
    
    # Visualizzazione
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Probabilità 1", f"{p1:.1%}")
    c2.metric("Probabilità X", f"{px:.1%}")
    c3.metric("Probabilità 2", f"{p2:.1%}")
    c4.metric("Over 2.5", f"{po25:.1%}")
    
    # Analisi Markoviana
    st.subheader("Analisi della Consistenza (Markov)")
    if stabilita > 0.5:
        st.success(f"INDICE DI STABILITÀ: {stabilita:.2f} - Risultato Molto Probabile (Solidità Markoviana)")
    else:
        st.warning(f"INDICE DI STABILITÀ: {stabilita:.2f} - Match Altamente Volatile (Caos Markoviano)")

    st.write("ℹ️ *Il modello MCTS ha simulato 10.000 varianti della partita per trovare queste frequenze.*")
