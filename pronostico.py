import streamlit as st
import numpy as np
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="GOTHIC SYNDICATE v6", layout="wide")

# --- STILE GOTHIC DARK ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, .gothic-title { font-family: 'UnifrakturMaguntia', cursive; color: #ffffff; text-align: center; font-size: 3.5rem !important; }
    .stButton>button { width: 100%; background-color: #fff; color: #000; font-weight: 900; border: 2px solid #ff0000; height: 3em; }
    .stButton>button:hover { background-color: #ff0000; color: #fff; }
    div[data-testid="stExpander"] { background-color: #111; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE MATEMATICO ---
def run_analysis_engine(xg_h, xga_h, elo_h, xg_a, xga_a, elo_a, q1, qX, q2, n_sim=20000):
    elo_diff = (elo_h - elo_a) / 1000
    mu_c = ((xg_h + xga_a) / 2) * (1 + elo_diff)
    mu_o = ((xg_a + xga_h) / 2) * (1 - elo_diff)
    
    sim_c = np.random.poisson(max(0.01, mu_c), n_sim)
    sim_o = np.random.poisson(max(0.01, mu_o), n_sim)
    
    p1 = np.sum(sim_c > sim_o) / n_sim
    px = np.sum(sim_c == sim_o) / n_sim
    p2 = np.sum(sim_c < sim_o) / n_sim
    
    # Calcolo Edge e Kelly per ogni segno
    def get_stats(prob, quota):
        if quota <= 1: return 0.0, 0.0
        edge = prob - (1/quota)
        b = quota - 1
        kelly = max(0, ((b * prob) - (1-prob)) / b)
        return edge, kelly

    e1, k1 = get_stats(p1, q1)
    eX, kX = get_stats(px, qX)
    e2, k2 = get_stats(p2, q2)
    
    return p1, px, p2, e1, k1, eX, kX, e2, k2

# --- INTERFACCIA ---
st.markdown('<div class="gothic-title">Gothic Syndicate: Full Market Edition</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 CARICA EXCEL (.XLSX)", "✍️ MANUALE"])

with tab1:
    uploaded_file = st.file_uploader("Carica il file Excel con le colonne: Home, Away, xG_Home, xGA_Home, ELO_Home, xG_Away, xGA_Away, ELO_Away, Quota1, QuotaX, Quota2", type="xlsx")
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        
        if st.button("PROCESSA PALINSESTO COMPLETO"):
            with st.spinner('Simulazione in corso...'):
                try:
                    res = df.apply(lambda r: run_analysis_engine(
                        r['xG_Home'], r['xGA_Home'], r['ELO_Home'],
                        r['xG_Away'], r['xGA_Away'], r['ELO_Away'],
                        r['Quota1'], r['QuotaX'], r['Quota2']
                    ), axis=1)
                    
                    cols = ['P_1', 'P_X', 'P_2', 'Edge_1', 'Kelly_1', 'Edge_X', 'Kelly_X', 'Edge_2', 'Kelly_2']
                    df[cols] = pd.DataFrame(res.tolist(), index=df.index)
                    
                    st.markdown("### 📜 RISULTATI COMPLETI")
                    # Mostriamo le colonne principali per non affollare lo schermo
                    view_cols = ['Home', 'Away', 'P_1', 'Edge_1', 'P_X', 'Edge_X', 'P_2', 'Edge_2']
                    
                    st.dataframe(df[view_cols].style.format({
                        'P_1': '{:.1%}', 'Edge_1': '{:.1%}',
                        'P_X': '{:.1%}', 'Edge_X': '{:.1%}',
                        'P_2': '{:.1%}', 'Edge_2': '{:.1%}'
                    }).background_gradient(subset=['Edge_1', 'Edge_X', 'Edge_2'], cmap='RdYlGn'))
                    
                except Exception as e:
                    st.error(f"Errore: verifica i nomi delle colonne nell'Excel. Dettaglio: {e}")

with tab2:
    st.info("Usa questa sezione per un calcolo rapido su un singolo match.")
    c1, c2, c3 = st.columns(3)
    with c1:
        xh = st.number_input("xG Casa", 1.5)
        eh = st.number_input("ELO Casa", 1500)
        q1 = st.number_input("Quota 1", 2.0)
    with c2:
        xa = st.number_input("xG Ospite", 1.2)
        ea = st.number_input("ELO Ospite", 1500)
        qX = st.number_input("Quota X", 3.2)
    with c3:
        qa_2 = st.number_input("Quota 2", 3.5)

    if st.button("CALCOLA SINGOLO"):
        p1, px, p2, e1, k1, eX, kX, e2, k2 = run_analysis_engine(xh, xh, eh, xa, xa, ea, q1, qX, qa_2)
        st.write(f"**Vantaggio 1:** {e1:.1%} | **Kelly:** {k1:.1%}")
        st.write(f"**Vantaggio X:** {eX:.1%} | **Kelly:** {kX:.1%}")
        st.write(f"**Vantaggio 2:** {e2:.1%} | **Kelly:** {k2:.1%}")

