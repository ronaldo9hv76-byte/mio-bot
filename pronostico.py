import streamlit as st
import numpy as np
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="GOTHIC SYNDICATE v8", layout="wide")

# --- STILE GOTHIC DARK ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, .gothic-title { font-family: 'UnifrakturMaguntia', cursive; color: #ffffff; text-align: center; font-size: 3rem !important; }
    .stButton>button { width: 100%; background-color: #fff; color: #000; font-weight: 900; border: 2px solid #ff0000; height: 3em; }
    .stButton>button:hover { background-color: #ff0000; color: #fff; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE MATEMATICO ---
def run_analysis_engine(xg_h, xga_h, elo_h, xg_a, xga_a, elo_a, q1, qX, q2, n_sim=20000):
    # Protezione dati vuoti
    vals = [xg_h, xga_h, elo_h, xg_a, xga_a, elo_a]
    xg_h, xga_h, elo_h, xg_a, xga_a, elo_a = [float(v) if str(v).strip() != '' else 0.0 for v in vals]
    
    elo_diff = (elo_h - elo_a) / 1000
    mu_c = ((xg_h + xga_a) / 2) * (1 + elo_diff)
    mu_o = ((xg_a + xga_h) / 2) * (1 - elo_diff)
    
    sim_c = np.random.poisson(max(0.01, mu_c), n_sim)
    sim_o = np.random.poisson(max(0.01, mu_o), n_sim)
    
    p1 = np.sum(sim_c > sim_o) / n_sim
    px = np.sum(sim_c == sim_o) / n_sim
    p2 = np.sum(sim_c < sim_o) / n_sim
    uo25 = np.sum((sim_c + sim_o) > 2.5) / n_sim
    
    def get_stats(prob, quota):
        if quota <= 1: return 0.0, 0.0
        edge = prob - (1/quota)
        b = quota - 1
        kelly = max(0, ((b * prob) - (1-prob)) / b) if b > 0 else 0
        return edge, kelly

    e1, k1 = get_stats(p1, q1)
    eX, kX = get_stats(px, qX)
    e2, k2 = get_stats(p2, q2)
    
    return p1, px, p2, e1, k1, eX, kX, e2, k2, uo25

# --- INTERFACCIA ---
st.markdown('<div class="gothic-title">Gothic Syndicate: Ultimate Version</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 ANALISI EXCEL", "✍️ MANUALE"])

with tab1:
    uploaded_file = st.file_uploader("Carica .xlsx", type="xlsx")
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file).fillna(0)
        
        if st.button("PROCESSA PALINSESTO"):
            with st.spinner('Calcolo in corso...'):
                try:
                    res = df.apply(lambda r: run_analysis_engine(
                        r['xG_Home'], r['xGA_Home'], r['ELO_Home'],
                        r['xG_Away'], r['xGA_Away'], r['ELO_Away'],
                        r['Quota1'], r['QuotaX'], r['Quota2']
                    ), axis=1)
                    
                    cols = ['P_1', 'P_X', 'P_2', 'Edge_1', 'Kelly_1', 'Edge_X', 'Kelly_X', 'Edge_2', 'Kelly_2', 'UO_Prob']
                    df[cols] = pd.DataFrame(res.tolist(), index=df.index)
                    
                    # Colonna Consigliata U/O 2.5
                    df['U/O 2,5'] = df['UO_Prob'].apply(lambda x: 'OVER' if x > 0.58 else 'UNDER')

                    st.markdown("### 📜 RISULTATI COMPLETI")
                    
                    # Visualizzazione tutte le colonne
                    view_cols = ['Home', 'Away', 'P_1', 'Edge_1', 'Kelly_1', 'P_X', 'Edge_X', 'Kelly_X', 'P_2', 'Edge_2', 'Kelly_2', 'U/O 2,5', 'UO_Prob']
                    
                    def color_uo(val):
                        color = 'background-color: green' if val == 'OVER' else 'background-color: red'
                        return color

                    st.dataframe(df[view_cols].style.format({
                        'P_1': '{:.1%}', 'Edge_1': '{:.1%}', 'Kelly_1': '{:.1%}',
                        'P_X': '{:.1%}', 'Edge_X': '{:.1%}', 'Kelly_X': '{:.1%}',
                        'P_2': '{:.1%}', 'Edge_2': '{:.1%}', 'Kelly_2': '{:.1%}',
                        'UO_Prob': '{:.1%}'
                    }).applymap(color_uo, subset=['U/O 2,5'])
                      .background_gradient(subset=['Edge_1', 'Edge_X', 'Edge_2'], cmap='RdYlGn'))
                    
                except Exception as e:
                    st.error(f"Errore: {e}")

with tab2:
    st.write("Inserimento manuale rapido...")
    # (Logica manuale semplificata omessa per brevità, focalizzata su Excel)
