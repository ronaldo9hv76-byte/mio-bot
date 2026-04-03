import streamlit as st
import math
import numpy as np

# --- CONFIGURAZIONE ESTETICA BLACK & WHITE ---
st.set_page_config(page_title="CORE-AI BET", layout="centered")

st.markdown("""
    <style>
    /* Sfondo totale nero e testo bianco */
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* Input e Sidebar */
    .stNumberInput input, .stTextInput input, .stSelectbox div {
        background-color: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
    
    /* Bottoni */
    .stButton>button {
        width: 100%;
        border-radius: 0px;
        height: 3.5em;
        background-color: #ffffff;
        color: #000000;
        border: none;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .stButton>button:hover { background-color: #cccccc; }
    
    /* Metriche */
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-family: monospace; font-size: 2.5rem; }
    div[data-testid="stMetricLabel"] { color: #888888 !important; text-transform: uppercase; }
    
    /* Expander e divisori */
    .streamlit-expanderHeader { background-color: #000000 !important; border: 1px solid #222 !important; }
    hr { border: 0.5px solid #222; }
    </style>
    """, unsafe_allow_html=True)

def mcts_core(mu_c, mu_o, n_sim=15000):
    v_c, p, v_o, o25 = 0, 0, 0, 0
    for _ in range(n_sim):
        g_c = np.random.poisson(max(0.05, mu_c))
        g_o = np.random.poisson(max(0.05, mu_o))
        if g_c > g_o: v_c += 1
        elif g_c == g_o: p += 1
        else: v_o += 1
        if (g_c + g_o) > 2.5: o25 += 1
    return v_c/n_sim, p/n_sim, v_o/n_sim, o25/n_sim

# --- INTERFACCIA PRINCIPALE ---
st.title("♟️ CORE-AI / PREDICTOR")
st.caption("ULTIMATE BLACK EDITION - MARKOV & MCTS INTEGRATION")

col1, col2 = st.columns(2)
with col1:
    st.overline("HOME")
    c_name = st.text_input("", "SQUADRA A", key="cn")
    c_xg = st.number_input("xGoals Fatti", value=1.5, key="cxg")
    c_corn = st.number_input("Media Corner", value=5, key="cc")

with col2:
    st.overline("AWAY")
    o_name = st.text_input("", "SQUADRA B", key="on")
    o_xg = st.number_input("xGoals Fatti ", value=1.2, key="oxg")
    o_corn = st.number_input("Media Corner ", value=4, key="oc")

st.markdown("---")

# --- PARAMETRI AVANZATI DEI BOOKMAKER ---
with st.expander("➕ PARAMETRI PROFESSIONALI (SNAI/BET365 LOGIC)"):
    st.write("Regola i pesi tattici basandoti sulle news dell'ultima ora.")
    f1, f2 = st.columns(2)
    with f1:
        forma_c = st.select_slider("Forma Team Casa", options=[1,2,3,4,5], value=3)
        pressione = st.checkbox("Pressione Alta / Pressing", value=False)
    with f2:
        forma_o = st.select_slider("Forma Team Ospite", options=[1,2,3,4,5], value=3)
        murales = st.checkbox("Difesa a Oltranza (Park the Bus)", value=False)

if st.button("Calculate Value"):
    # Logica di calcolo raffinata
    # I corner pesano per un 5% sulla pericolosità
    peso_c = c_xg + (c_corn * 0.05)
    peso_o = o_xg + (o_corn * 0.05)
    
    # Moltiplicatori Forma (base 3)
    peso_c *= (forma_c / 3)
    peso_o *= (forma_o / 3)
    
    # Tattica
    if pressione: peso_c *= 1.15
    if murales: peso_o *= 0.8
    
    # Simulazione
    p1, px, p2, o25 = mcts_core(peso_c, peso_o)
    markov_stabiliy = (p1**2 + px**2 + p2**2)

    # OUTPUT
    st.markdown("### 🏁 PREDICTION RESULTS")
    res1, res2, res3 = st.columns(3)
    res1.metric("HOME", f"{p1:.1%}")
    res2.metric("DRAW", f"{px:.1%}")
    res3.metric("AWAY", f"{p2:.1%}")
    
    st.markdown("---")
    
    val1, val2 = st.columns(2)
    with val1:
        st.write("**PROBABILITÀ OVER 2.5**")
        st.header(f"{o25:.1%}")
    with val2:
        st.write("**STABILITÀ MARKOV**")
        status = "SOLID" if markov_stabiliy > 0.48 else "VOLATILE"
        st.header(status)
        st.caption(f"Score: {markov_stabiliy:.2f}")

    if o25 > 0.65:
        st.success("TARGET DETECTED: HIGH PROBABILITY OVER 2.5")
    elif p1 > 0.55:
        st.success(f"TARGET DETECTED: DOMINANCE {c_name}")
