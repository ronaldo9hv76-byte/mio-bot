import streamlit as st
import numpy as np
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="GOTHIC SYNDICATE v8.5", layout="wide")

# --- STILE CSS PERSONALIZZATO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, .gothic-title { 
        font-family: 'UnifrakturMaguntia', cursive; 
        color: #ffffff; 
        text-align: center; 
        font-size: 3.5rem !important;
        text-shadow: 2px 2px #ff0000;
        margin-bottom: 30px;
    }
    .stButton>button { 
        width: 100%; 
        background-color: #1a1a1a; 
        color: white; 
        font-weight: 900; 
        border: 1px solid #ff0000;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff0000;
        color: black;
        border: 1px solid #ffffff;
    }
    /* Stile per tabelle Streamlit */
    .stDataFrame { border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

def run_analysis_engine(row, n_sim=20000):
    try:
        # Funzione di pulizia per gestire stringhe, virgole e valori nulli
        def clean_val(val):
            if pd.isna(val): return 1.2
            if isinstance(val, str):
                val = val.replace(',', '.')
            v = float(val)
            return v if v > 0 else 1.2

        xh = clean_val(row['xG_Home'])
        xah = clean_val(row['xGA_Home'])
        eh = clean_val(row['ELO_Home'])
        xa = clean_val(row['xG_Away'])
        xaa = clean_val(row['xGA_Away'])
        ea = clean_val(row['ELO_Away'])
        q1 = clean_val(row['Quota1'])
        qX = clean_val(row['QuotaX'])
        q2 = clean_val(row['Quota2'])
        
        # Algoritmo di Bilanciamento Lambda (Poisson)
        # Il differenziale ELO influenza la proiezione degli xG
        elo_diff = (eh - ea) / 400
        lambda_h = ((xh + xaa) / 2) * (1.2 ** elo_diff)
        lambda_a = ((xa + xah) / 2) * (1.2 ** -elo_diff)
        
        # Simulazione Monte Carlo
        sim_h = np.random.poisson(max(0.01, lambda_h), n_sim)
        sim_a = np.random.poisson(max(0.01, lambda_a), n_sim)
        
        # Calcolo Probabilità
        p1 = np.sum(sim_h > sim_a) / n_sim
        px = np.sum(sim_h == sim_a) / n_sim
        p2 = np.sum(sim_h < sim_a) / n_sim
        uo25_prob = np.sum((sim_h + sim_a) > 2.5) / n_sim
        
        # Logica di Valore (Edge & Kelly)
        def get_stats(prob, quota):
            if quota <= 1: return 0.0, 0.0
            edge = prob - (1/quota)
            b = quota - 1
            # Kelly Criterion (frazione del bankroll consigliata)
            kelly = ((b * prob) - (1 - prob)) / b
            return edge, max(0, kelly)

        e1, k1 = get_stats(p1, q1)
        eX, kX = get_stats(px, qX)
        e2, k2 = get_stats(p2, q2)
        
        return p1, px, p2, e1, k1, eX, kX, e2, k2, uo25_prob
    except Exception as e:
        return [0.0]*10

# --- INTERFACCIA UTENTE ---
st.markdown('<div class="gothic-title">Gothic Syndicate: V8.5 Pro</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    uploaded_file = st.file_uploader("📂 Carica il Palinsesto Excel (.xlsx)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Pre-elaborazione colonne per evitare errori di tipo
    cols_to_fix = ['xG_Home', 'xGA_Home', 'ELO_Home', 'xG_Away', 'xGA_Away', 'ELO_Away', 'Quota1', 'QuotaX', 'Quota2']
    for col in cols_to_fix:
        if col in df.columns and df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(',', '.').astype(float)

    if st.button("🔥 PROCESSA PALINSESTO"):
        with st.spinner('Simulazione Poisson in corso...'):
            # Applica il motore di calcolo
            res = df.apply(run_analysis_engine, axis=1)
            
            # Espansione risultati
            res_cols = ['P_1', 'P_X', 'P_2', 'Edge_1', 'Kelly_1', 'Edge_X', 'Kelly_X', 'Edge_2', 'Kelly_2', 'UO_Prob']
            df_res = pd.DataFrame(res.tolist(), index=df.index, columns=res_cols)
            df = pd.concat([df, df_res], axis=1)
            
            # Definizione Under/Over
            df['U/O 2,5'] = df['UO_Prob'].apply(lambda x: 'OVER' if x > 0.58 else 'UNDER')
            
            # Selezione colonne per visualizzazione finale
            view = ['Home', 'Away', 'P_1', 'Edge_1', 'Kelly_1', 'P_X', 'Edge_X', 'P_2', 'Edge_2', 'U/O 2,5', 'UO_Prob']
            
            # Formattazione condizionale e visualizzazione
            st.dataframe(
                df[view].style.format({
                    'P_1': '{:.1%}', 'Edge_1': '{:.1%}', 'Kelly_1': '{:.1%}',
                    'P_X': '{:.1%}', 'Edge_X': '{:.1%}', 'Kelly_X': '{:.1%}',
                    'P_2': '{:.1%}', 'Edge_2': '{:.1%}', 'Kelly_2': '{:.1%}',
                    'UO_Prob': '{:.1%}'
                }).map(
                    lambda x: f'background-color: {"#006400" if x == "OVER" else "#8B0000"}; color: white; font-weight: bold', 
                    subset=['U/O 2,5']
                ).background_gradient(
                    subset=['Edge_1', 'Edge_X', 'Edge_2'], 
                    cmap='RdYlGn'
                )
            )
            
            st.success("Analisi completata. Le celle in VERDE indicano un valore statistico (Edge).")
