import streamlit as st
import numpy as np
import pandas as pd

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="GOTHIC ORACLE v9.5 SYNDICATE", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, .gothic-title { font-family: 'UnifrakturMaguntia', cursive; color: #ff0000; text-align: center; font-size: 3.5rem !important; }
    .stButton>button { width: 100%; background-color: #333; color: #fff; font-weight: 900; border: 1px solid #ff0000; }
    </style>
    """, unsafe_allow_html=True)

def analyze_full_syndicate(row, n_sim=30000):
    try:
        def clean(val):
            if pd.isna(val): return 1.2
            if isinstance(val, str): val = val.replace(',', '.')
            v = float(val)
            return v if v > 0 else 1.2

        xh, xah, eh = clean(row['xG_Home']), clean(row['xGA_Home']), clean(row['ELO_Home'])
        xa, xaa, ea = clean(row['xG_Away']), clean(row['xGA_Away']), clean(row['ELO_Away'])
        q1, qX, q2 = clean(row['Quota1']), clean(row['QuotaX']), clean(row['Quota2'])
        
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

        # 2. MARKOV STABILITY INDEX
        prob_dominance = 1 / (1 + np.exp(-(abs(eh - ea)/250)))
        prob_scoring_efficiency = (xh + xa) / (xh + xa + xah + xaa + 0.1)
        markov_index = (prob_dominance * 0.6) + (prob_scoring_efficiency * 0.4)

        # 3. EDGE CALCULATION (VALUE BETTING)
        # Calcoliamo l'edge sul segno più probabile indicato dal bot
        if p1 > px and p1 > p2:
            best_p, best_q, label = p1, q1, "1"
        elif p2 > p1 and p2 > px:
            best_p, best_q, label = p2, q2, "2"
        else:
            best_p, best_q, label = px, qX, "X"
            
        edge = (best_p * best_q) - 1

        return p1, px, p2, p_goal, p_uo25, markov_index, edge, label
    except:
        return [0.33, 0.33, 0.33, 0.5, 0.5, 0.5, 0, "N/A"]

st.markdown('<div class="gothic-title">Gothic Oracle v9.5: The Syndicate</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Carica Excel (Richiede xG, ELO e QUOTE)", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Pulizia colonne numeriche inclusi i bookmaker
    num_cols = ['xG_Home', 'xGA_Home', 'ELO_Home', 'xG_Away', 'xGA_Away', 'ELO_Away', 'Quota1', 'QuotaX', 'Quota2']
    for col in num_cols:
        if col in df.columns and df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(',', '.').astype(float)

    if st.button("🔥 ESEGUI ANALISI TOTALE"):
        res = df.apply(analyze_full_syndicate, axis=1)
        res_df = pd.DataFrame(res.tolist(), columns=['P1', 'PX', 'P2', 'P_GOAL', 'P_UO25', 'MARKOV_VAL', 'EDGE', 'BEST_SIGN'], index=df.index)
        
        df = df.reset_index(drop=True)
        res_df = res_df.reset_index(drop=True)
        df = pd.concat([df, res_df], axis=1)
        
        # LOGICA ESITI
        df['GOAL/NOGOAL'] = df['P_GOAL'].apply(lambda x: 'GOAL' if x > 0.52 else 'NO GOAL')
        df['U/O 2,5'] = df['P_UO25'].apply(lambda x: 'OVER 2.5' if x > 0.609 else 'UNDER 2.5')
        df['STABILITÀ'] = df['MARKOV_VAL'].apply(lambda x: 'ALTA 🔒' if x > 0.65 else ('MEDIA ⚠️' if x > 0.45 else 'BASSA 🧨'))
        
        # Visualizzazione colonne
        view = ['Home', 'Away', 'BEST_SIGN', 'EDGE', 'GOAL/NOGOAL', 'U/O 2,5', 'STABILITÀ', 'MARKOV_VAL']
        
        def apply_style(val, column_name):
            if column_name == 'EDGE':
                return 'background-color: #006400; color: white' if val > 0.05 else 'background-color: #8B0000; color: white'
            if any(char in str(val) for char in ['GOAL', 'OVER', '1', '2', 'ALTA']):
                return 'background-color: #006400; color: white; font-weight: bold'
            if 'BASSA' in str(val) or '🧨' in str(val):
                return 'background-color: #ff4b4b; color: black; font-weight: bold'
            return 'background-color: #8B0000; color: white; font-weight: bold'

        styled_df = df[view].style.format({
            'MARKOV_VAL': '{:.1%}',
            'EDGE': '{:.1%}'
        }).map(lambda x: apply_style(x, 'EDGE'), subset=['EDGE'])\
          .map(lambda x: apply_style(x, 'OTHER'), subset=['GOAL/NOGOAL', 'U/O 2,5', 'STABILITÀ', 'BEST_SIGN'])
        
        st.dataframe(styled_df, use_container_width=True)
        st.success("Analisi completata: Previsione, Stabilità e Valore economico integrati.")
