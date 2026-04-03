import streamlit as st
import math
import numpy as np

# --- CONFIGURAZIONE ESTETICA BLACK & WHITE ---
st.set_page_config(page_title="CORE-AI BET", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    .stNumberInput input, .stTextInput input, .stSelectbox div {
        background-color: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
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
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-family: monospace; font-size: 2.5rem; }
    div[data-testid="stMetricLabel"] { color: #888888 !important; text-transform: uppercase; }
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
    st.markdown("### HOME")
    c_name = st.text_input("Team", "SQUADRA A", key="cn")
    c_xg = st.number_input("xGoals Fatti", value=1.5, key="cxg")
    c_corn = st.number_input("Media Corner", value=5, key="cc")

with col2:
    st.markdown("### AWAY")
    o_name = st.text_input("Team ", "SQUADRA B", key="on")
    o_xg = st.number_input("xGoals Fatti ", value=1.2, key="oxg")
    o_corn = st.number_input("Media Corner ", value=4, key="oc")

st.markdown("---")

with st.expander("➕ PARAMETRI PROFESSIONALI"):
    f1, f2 = st.columns(2)
    with f1:
        forma_c = st.select_slider("Forma Casa", options=[1,2,3,4,5], value=3)
        pressione = st.checkbox("Pressing Alto", value=False)
    with f2:
        forma_o = st.select_slider("Forma Ospite", options=[1,2,3,4,5], value=3)
        murales = st.checkbox("Difesa Oltranza", value=False)

if st.button("Calculate Value"):
    peso_c = c_xg + (c_corn * 0.05)
    peso_o = o_xg + (o_corn * 0.05)
    peso_c *= (forma_c / 3)
    peso_o *= (forma_o / 3)
    if pressione: peso_c *= 1.15
    if murales: peso_o *= 0.8
    
    p1, px, p2, o25 = mcts_core(peso_c, peso_o)
    markov_stabiliy = (p1**2 + px**2 + p2**2)

    st.markdown("### 🏁 PREDICTION RESULTS")
    res1, res2, res3 = st.columns(3)
    res1.metric("HOME", f"{p1:.1%}")
    res2.metric("DRAW", f"{px:.1%}")
    res3.metric("AWAY", f"{p2:.1%}")
    
    st.markdown("---")
    
    val1, val2 = st.columns(2)
    with val1:
        st.write("**OVER 2.5**")
        st.header(f"{o25:.1%}")
    with val2:
        st.write("**STABILITÀ MARKOV**")
        status = "SOLID" if markov_stabiliy > 0.48 else "VOLATILE"
        st.header(status)
