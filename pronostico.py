import streamlit as st
import numpy as np
import pandas as pd

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="GOTHIC ORACLE v9.0", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, .gothic-title { font-family: 'UnifrakturMaguntia', cursive; color: #ff0000; text-align: center; font-size: 3.5rem !important; }
    .stButton>button { width: 100%; background-color: #333; color: #fff; font-weight: 900; border: 1px solid #ff0000; }
    </style>
    """, unsafe_allow_html=True)

def oracle_engine(row, n_sim=30000):
    try:
        def clean(val):
            if pd.isna(val): return 1.2
            if isinstance(val, str): val = val.replace(',', '.')
            return float(val)

        xh, xah, eh = clean(row['xG_Home']), clean(row['xGA_Home']), clean(row['ELO_Home'])
        xa, xaa, ea = clean(row['xG_Away']), clean(row['xGA_Away']), clean(row['ELO_Away'])
        
        # Motore di simulazione Poisson
        elo_diff = (eh - ea) / 400
        lambda_h = ((xh + xaa) / 2) * (1.2 ** elo_diff)
        lambda_a = ((xa + xah) / 2) * (1.2 ** -elo_diff)
        
        sh = np.random.poisson(max(0.01, lambda_h), n_sim)
        sa = np.random.poisson(max(0.01, lambda_a), n_sim)
        stot = sh + sa
        
        # --- CALCOLO PROBABILITÀ ---
        # Esiti 1X2
        p1, px, p2 = np.sum(sh > sa)/n_sim, np.sum(sh == sa)/n_sim, np.sum(sh < sa)/n_sim
        
        # Goal / No Goal
        p_goal = np.sum((sh > 0) & (sa > 0)) / n_sim
        
        # Multigol
        p_m13 = np.sum((stot >= 1) & (stot <= 3)) / n_sim
        p_m24 = np.sum((stot >= 2) & (stot <= 4)) / n_sim
        
        # Under / Over 2.5
        p_uo25 = np.sum(stot > 2.5) / n_sim

        return p1, px, p2, p_goal, p_m13, p_m24, p_uo25
    except:
        return [0.0]*7

st.markdown('<div class="gothic-title">Gothic Oracle: Predizioni Pure</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Carica Excel (Richiesti solo xG, xGA, ELO)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    if st.button("🔮 GENERA PREVISIONI"):
        res = df.apply(oracle_engine, axis=1)
        cols = ['P1', 'PX', 'P2', 'P_GOAL', 'P_M13', 'P_M24', 'P_UO25']
        df[cols] = pd.DataFrame(res.tolist(), index=df.index)
        
        # Traduzione in suggerimenti testuali
        df['GOAL/NOGOAL'] = df['P_GOAL'].apply(lambda x: 'GOAL' if x > 0.52 else 'NO GOAL')
        df['MULTIGOL 1-3'] = df['P_M13'].apply(lambda x: 'M 1-3 ✅' if x > 0.52 else 'M 1-3 ❌')
        df['MULTIGOL 2-4'] = df['P_M24'].apply(lambda x: 'M 2-4 ✅' if x > 0.52 else 'M 2-4 ❌')
        df['ESITO 1X2'] = df.apply(lambda r: '1' if r['P1']>r['PX'] and r['P1']>r['P2'] else ('X' if r['PX']>r['P2'] else '2'), axis=1)

        # Visualizzazione
        view = ['Home', 'Away', 'ESITO 1X2', 'GOAL/NOGOAL', 'MULTIGOL 1-3', 'MULTIGOL 2-4', 'P_UO25']
        
        def style_prediction(val):
            # Colora di verde se la previsione è positiva (contiene spunta o è Goal/1)
            if any(x in str(val) for x in ['✅', 'GOAL', '1', '2']):
                return 'background-color: #006400; color: white'
            return 'background-color: #8B0000; color: white'

        st.dataframe(df[view].style.format({'P_UO25': '{:.1%}'}).applymap(style_prediction, subset=['GOAL/NOGOAL', 'MULTIGOL 1-3', 'MULTIGOL 2-4']))
        
        st.info("Nota: Il verde indica una probabilità statistica superiore al 52%. Il rosso indica un esito incerto o poco probabile.")
