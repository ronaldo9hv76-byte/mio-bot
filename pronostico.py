import streamlit as st
import numpy as np
import pandas as pd

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="GOTHIC ORACLE v9.1", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, .gothic-title { font-family: 'UnifrakturMaguntia', cursive; color: #ff0000; text-align: center; font-size: 3.5rem !important; }
    .stButton>button { width: 100%; background-color: #333; color: #fff; font-weight: 900; border: 1px solid #ff0000; }
    </style>
    """, unsafe_allow_html=True)

def oracle_engine(row, n_sim=20000):
    try:
        def clean(val):
            if pd.isna(val): return 1.2
            if isinstance(val, str): val = val.replace(',', '.')
            v = float(val)
            return v if v > 0 else 1.2

        xh, xah, eh = clean(row['xG_Home']), clean(row['xGA_Home']), clean(row['ELO_Home'])
        xa, xaa, ea = clean(row['xG_Away']), clean(row['xGA_Away']), clean(row['ELO_Away'])
        
        elo_diff = (eh - ea) / 400
        lambda_h = ((xh + xaa) / 2) * (1.2 ** elo_diff)
        lambda_a = ((xa + xah) / 2) * (1.2 ** -elo_diff)
        
        sh = np.random.poisson(max(0.01, lambda_h), n_sim)
        sa = np.random.poisson(max(0.01, lambda_a), n_sim)
        stot = sh + sa
        
        p1 = np.sum(sh > sa)/n_sim
        px = np.sum(sh == sa)/n_sim
        p2 = np.sum(sh < sa)/n_sim
        p_goal = np.sum((sh > 0) & (sa > 0)) / n_sim
        p_m13 = np.sum((stot >= 1) & (stot <= 3)) / n_sim
        p_m24 = np.sum((stot >= 2) & (stot <= 4)) / n_sim
        p_uo25 = np.sum(stot > 2.5) / n_sim

        return p1, px, p2, p_goal, p_m13, p_m24, p_uo25
    except:
        return [0.5, 0.2, 0.3, 0.5, 0.5, 0.5, 0.5]

st.markdown('<div class="gothic-title">Gothic Oracle: Predizioni Fixed</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Carica Excel", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Pre-pulizia dati colonne numeriche
    num_cols = ['xG_Home', 'xGA_Home', 'ELO_Home', 'xG_Away', 'xGA_Away', 'ELO_Away']
    for col in num_cols:
        if col in df.columns and df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(',', '.').astype(float)

    if st.button("🔮 GENERA PREVISIONI"):
        res = df.apply(oracle_engine, axis=1)
        res_df = pd.DataFrame(res.tolist(), columns=['P1', 'PX', 'P2', 'P_GOAL', 'P_M13', 'P_M24', 'P_UO25'], index=df.index)
        df = pd.concat([df, res_df], axis=1)
        
        # Logica esiti
        df['GOAL/NOGOAL'] = df['P_GOAL'].apply(lambda x: 'GOAL' if x > 0.52 else 'NO GOAL')
        df['MULTIGOL 1-3'] = df['P_M13'].apply(lambda x: '1-3 ✅' if x > 0.55 else '1-3 ❌')
        df['MULTIGOL 2-4'] = df['P_M24'].apply(lambda x: '2-4 ✅' if x > 0.55 else '2-4 ❌')
        df['PREVISIONE 1X2'] = df.apply(lambda r: '1' if r['P1']>r['PX'] and r['P1']>r['P2'] else ('2' if r['P2']>r['P1'] and r['P2']>r['PX'] else 'X'), axis=1)

        view = ['Home', 'Away', 'PREVISIONE 1X2', 'GOAL/NOGOAL', 'MULTIGOL 1-3', 'MULTIGOL 2-4', 'P_UO25']
        
        # Nuova funzione di stile compatibile con le ultime versioni di Pandas
        def apply_style(val):
            color = '#006400' if any(char in str(val) for char in ['✅', 'GOAL', '1', '2']) else '#8B0000'
            return f'background-color: {color}; color: white; font-weight: bold'

        # Visualizzazione con .map() invece di .applymap()
        styled_df = df[view].style.format({'P_UO25': '{:.1%}'}).map(apply_style, subset=['GOAL/NOGOAL', 'MULTIGOL 1-3', 'MULTIGOL 2-4'])
        
        st.dataframe(styled_df, use_container_width=True)
        st.success("Analisi completata con successo.")
