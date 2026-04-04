import streamlit as st
import numpy as np
import pandas as pd

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="GOTHIC ORACLE v9.4 PLATINUM", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, .gothic-title { font-family: 'UnifrakturMaguntia', cursive; color: #ff0000; text-align: center; font-size: 3.5rem !important; }
    .stButton>button { width: 100%; background-color: #333; color: #fff; font-weight: 900; border: 1px solid #ff0000; }
    </style>
    """, unsafe_allow_html=True)

def analyze_engine_pro(row, n_sim=30000):
    try:
        def clean(val):
            if pd.isna(val): return 1.2
            if isinstance(val, str): val = val.replace(',', '.')
            v = float(val)
            return v if v > 0 else 1.2

        xh, xah, eh = clean(row['xG_Home']), clean(row['xGA_Home']), clean(row['ELO_Home'])
        xa, xaa, ea = clean(row['xG_Away']), clean(row['xGA_Away']), clean(row['ELO_Away'])
        
        # 1. POISSON ENGINE
        elo_diff = (eh - ea) / 400
        l_h = ((xh + xaa) / 2) * (1.2 ** elo_diff)
        l_a = ((xa + xah) / 2) * (1.2 ** -elo_diff)
        
        sh = np.random.poisson(l_h, n_sim)
        sa = np.random.poisson(l_a, n_sim)
        stot = sh + sa
        
        p1, px, p2 = np.sum(sh > sa)/n_sim, np.sum(sh == sa)/n_sim, np.sum(sh < sa)/n_sim
        p_goal = np.sum((sh > 0) & (sa > 0)) / n_sim
        p_uo25 = np.sum(stot > 2.5) / n_sim

        # 2. MARKOV STABILITY INDEX (Simulazione transizione di stato)
        # Calcoliamo la probabilità di transizione basata sulla dominanza ELO e xG
        # Rappresenta la capacità di mantenere lo stato di vantaggio
        prob_stay_win = 1 / (1 + np.exp(-(eh - ea)/200))
        prob_stay_draw = 1 - (abs(xh - xa) / (xh + xa + 0.1))
        markov_index = (prob_stay_win * 0.7) + (prob_stay_draw * 0.3)

        return p1, px, p2, p_goal, p_uo25, markov_index
    except:
        return [0.33, 0.33, 0.33, 0.5, 0.5, 0.5]

st.markdown('<div class="gothic-title">Gothic Oracle v9.4: Markov Edition</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Carica Excel", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Pulizia dati
    num_cols = ['xG_Home', 'xGA_Home', 'ELO_Home', 'xG_Away', 'xGA_Away', 'ELO_Away']
    for col in num_cols:
        if col in df.columns and df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(',', '.').astype(float)

    if st.button("🔮 ANALISI PREDITTIVA AVANZATA"):
        res = df.apply(analyze_engine_pro, axis=1)
        res_df = pd.DataFrame(res.tolist(), columns=['P1', 'PX', 'P2', 'P_GOAL', 'P_UO25', 'MARKOV'], index=df.index)
        df = pd.concat([df, res_df], axis=1)
        
        # LOGICA ESITI
        df['GOAL/NOGOAL'] = df['P_GOAL'].apply(lambda x: 'GOAL' if x > 0.52 else 'NO GOAL')
        df['U/O 2,5'] = df['P_UO25'].apply(lambda x: 'OVER 2.5' if x > 0.609 else 'UNDER 2.5')
        df['STABILITÀ'] = df['MARKOV'].apply(lambda x: 'ALTA 🔒' if x > 0.65 else ('MEDIA ⚠️' if x > 0.45 else 'BASSA 🧨'))
        df['PREVISIONE 1X2'] = df.apply(lambda r: '1' if r['P1']>r['PX'] and r['P1']>r['P2'] else ('2' if r['P2']>r['P1'] and r['P2']>r['PX'] else 'X'), axis=1)

        view = ['Home', 'Away', 'PREVISIONE 1X2', 'GOAL/NOGOAL', 'U/O 2,5', 'STABILITÀ', 'MARKOV']
        
        def apply_style(val):
            if any(char in str(val) for char in ['GOAL', 'OVER', '1', '2', 'ALTA']):
                return 'background-color: #006400; color: white; font-weight: bold'
            if 'BASSA' in str(val) or '🧨' in str(val):
                return 'background-color: #ff4b4b; color: black; font-weight: bold'
            return 'background-color: #8B0000; color: white; font-weight: bold'

        styled_df = df[view].style.format({'MARKOV': '{:.2f}'}).map(apply_style, subset=['GOAL/NOGOAL', 'U/O 2,5', 'STABILITÀ'])
        
        st.dataframe(styled_df, use_container_width=True)
        st.info("L'Indice di Markov indica la solidità del pronostico. Se è BASSA, aspettati sorprese indipendentemente dalle percentuali.")
