import streamlit as st
import numpy as np
import pandas as pd

# --- STYLE GOTHIC DARK ---
st.set_page_config(page_title="GOTHIC SYNDICATE v5", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, .gothic-title { font-family: 'UnifrakturMaguntia', cursive; color: #ffffff; text-align: center; font-size: 3.5rem !important; }
    .stButton>button { width: 100%; background-color: #fff; color: #000; font-weight: 900; border: 2px solid #ff0000; }
    .stButton>button:hover { background-color: #ff0000; color: #fff; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE MATEMATICO ---
def run_analysis(row, n_sim=20000):
    # Dati dalla riga dell'Excel
    # mu_c e mu_o calcolano i gol attesi medi (Poisson Lambda)
    mu_c = ((row['xG_Home'] + row['xGA_Away']) / 2) * (1 + (row['ELO_Home'] - row['ELO_Away'])/1000)
    mu_o = ((row['xG_Away'] + row['xGA_Home']) / 2) * (1 - (row['ELO_Home'] - row['ELO_Away'])/1000)
    
    sim_c = np.random.poisson(max(0.01, mu_c), n_sim)
    sim_o = np.random.poisson(max(0.01, mu_o), n_sim)
    
    p1 = np.sum(sim_c > sim_o) / n_sim
    px = np.sum(sim_c == sim_o) / n_sim
    p2 = np.sum(sim_c < sim_o) / n_sim
    
    # Kelly & Edge sul Segno 1
    implied_1 = 1 / row['Quota1']
    edge = p1 - implied_1
    b = row['Quota1'] - 1
    kelly = max(0, ((b * p1) - (1-p1)) / b) if row['Quota1'] > 1 else 0
    
    return pd.Series([f"{p1:.1%}", f"{px:.1%}", f"{p2:.1%}", f"{edge:.1%}", f"{kelly:.2%}"])

# --- INTERFACCIA ---
st.markdown('<div class="gothic-title">Gothic Syndicate: Excel Edition</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 CARICA EXCEL (.XLSX)", "✍️ MANUALE"])

with tab1:
    # MODIFICA: Accetta ora file .xlsx
    uploaded_file = st.file_uploader("Trascina qui il tuo file Excel del weekend", type="xlsx")
    
    if uploaded_file:
        # MODIFICA: Legge file Excel invece di CSV
        df = pd.read_excel(uploaded_file)
        
        if st.button("PROCESSA PALINSESTO EXCEL"):
            with st.spinner('L’Oracolo sta simulando migliaia di scenari...'):
                results = df.apply(run_analysis, axis=1)
                results.columns = ['Prob_1', 'Prob_X', 'Prob_2', 'Edge_1', 'Kelly_1']
                final_df = pd.concat([df[['Home', 'Away', 'Quota1']], results], axis=1)
                
                st.markdown("### 📜 ANALISI QUANTITATIVA COMPLETATA")
                # Visualizzazione con colori per evidenziare il valore
                st.dataframe(final_df.style.background_gradient(subset=['Edge_1'], cmap='RdYlGn'))
                st.info("I valori in verde scuro indicano un vantaggio matematico rispetto al banco.")

with tab2:
    st.write("Sezione manuale per test rapidi.")
    # (Qui puoi rimettere il codice per l'input singolo se ti serve ancora)
