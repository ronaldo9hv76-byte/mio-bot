import streamlit as st
import numpy as np

# --- CONFIGURAZIONE ESTETICA GOTHIC DARK ---
st.set_page_config(page_title="GOTHIC CORE-AI", layout="centered")

# Import Google Font: UnifrakturMaguntia (Gothic style)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Old+Standard+TT:italic,bold&display=swap');

    .stApp { background-color: #000000; color: #e0e0e0; }
    
    /* Font Gotico per i Titoli */
    h1, h2, .gothic-title {
        font-family: 'UnifrakturMaguntia', cursive;
        color: #ffffff;
        font-size: 3.5rem !important;
        text-shadow: 2px 2px 4px #444;
        text-align: center;
    }

    /* Font per il resto del testo */
    * { font-family: 'Old Standard TT', serif; }

    /* Input e Sidebar Black Edition */
    .stNumberInput input, .stTextInput input, .stSelectbox div {
        background-color: #0a0a0a !important;
        color: #ffffff !important;
        border: 1px solid #222 !important;
    }

    /* Bottone Monumentale */
    .stButton>button {
        width: 100%;
        border-radius: 0px;
        height: 4em;
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #ffffff;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 3px;
        transition: 0.5s;
    }
    .stButton>button:hover { background-color: #444; color: #fff; }

    /* Metriche */
    div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2.8rem; border-bottom: 1px solid #333; }
    hr { border: 0.5px solid #333; }
    </style>
    """, unsafe_allow_html=True)

def mcts_ultra_engine(mu_c, mu_o, n_sim=20000):
    """Simulazione MCTS ad alta densità"""
    v_c, p, v_o, o25 = 0, 0, 0, 0
    sim_c = np.random.poisson(max(0.01, mu_c), n_sim)
    sim_o = np.random.poisson(max(0.01, mu_o), n_sim)
    
    v_c = np.sum(sim_c > sim_o)
    p = np.sum(sim_c == sim_o)
    v_o = np.sum(sim_c < sim_o)
    o25 = np.sum((sim_c + sim_o) > 2.5)
    
    return v_c/n_sim, p/n_sim, v_o/n_sim, o25/n_sim

# --- INTERFACCIA ---
st.markdown('<div class="gothic-title">Gothic Core-AI</div>', unsafe_allow_html=True)
st.caption("THE ULTIMATE PRE-MATCH PROGNOSTICATOR")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🏰 Home Sanctum")
    name_c = st.text_input("Nome Squadra", "HOME TEAM", key="nc")
    xg_c = st.number_input("xG Attacco (Stagione)", value=1.6, key="xc")
    xga_c = st.number_input("xG Difesa (Subiti)", value=1.0, key="xac")
    corn_c = st.number_input("Corner Medi", value=5, key="cc")

with col2:
    st.markdown("### ⚔️ Away Invaders")
    name_o = st.text_input("Nome Squadra ", "AWAY TEAM", key="no")
    xg_o = st.number_input("xG Attacco (Stagione) ", value=1.3, key="xo")
    xga_o = st.number_input("xG Difesa (Subiti) ", value=1.2, key="xao")
    corn_o = st.number_input("Corner Medi ", value=4, key="co")

st.markdown("---")

with st.expander("🕯️ VARIABILI OCCULTE (BOOKMAKER LOGIC)"):
    f1, f2 = st.columns(2)
    with f1:
        st.write("**Fattori Interni**")
        forma_c = st.select_slider("Stato di Forma (1-5)", options=[1,2,3,4,5], value=3, key="f1")
        motivazione_c = st.select_slider("Importanza Match", options=["Bassa", "Media", "Vitale"], value="Media")
        assenze_c = st.selectbox("Infortunati Chiave", ["Nessuno", "1-2 Giocatori", "Assenze Gravi"], key="a1")
    with f2:
        st.write("**Fattori Esterni**")
        forma_o = st.select_slider("Stato di Forma (1-5) ", options=[1,2,3,4,5], value=3, key="f2")
        field_advantage = st.checkbox("Fattore Campo (Pubblico Caldo)", value=True)
        tattica_o = st.selectbox("Atteggiamento", ["Equilibrato", "Bus davanti alla porta", "Contropiede"], key="t2")

if st.button("Invoke Prediction"):
    # Logica Matematica Superiore
    mu_c = (xg_c + xga_o) / 2
    mu_o = (xg_o + xga_c) / 2
    
    # Applicazione Moltiplicatori
    # 1. Forma (Base 3)
    mu_c *= (forma_c / 3)
    mu_o *= (forma_o / 3)
    
    # 2. Corner (Pressione)
    mu_c += (corn_c * 0.04)
    mu_o += (corn_o * 0.04)
    
    # 3. Importanza/Motivazione
    if motivazione_c == "Vitale": mu_c *= 1.2
    
    # 4. Assenze
    if assenze_c == "Assenze Gravi": mu_c *= 0.8
    
    # 5. Fattore Campo
    if field_advantage: mu_c *= 1.1
    
    # 6. Tattica Ospite
    if tattica_o == "Bus davanti alla porta":
        mu_o *= 0.7
        mu_c *= 0.85 # Partita bloccata
        
    # Esecuzione MCTS 20k
    p1, px, p2, o25 = mcts_ultra_engine(mu_c, mu_o)
    markov = (p1**2 + px**2 + p2**2)

    # OUTPUT FINALE
    st.markdown("---")
    st.markdown(f"## {name_c} vs {name_o}")
    
    r1, r2, r3 = st.columns(3)
    r1.metric("CHANCE 1", f"{p1:.1%}")
    r2.metric("CHANCE X", f"{px:.1%}")
    r3.metric("CHANCE 2", f"{p2:.1%}")
    
    st.markdown("---")
    
    v1, v2 = st.columns(2)
    with v1:
        st.write("**PROBABILITÀ OVER 2.5**")
        st.header(f"{o25:.1%}")
    with v2:
        st.write("**STABILITÀ MARKOV**")
        status = "STABLE" if markov > 0.48 else "CHAOTIC"
        st.header(status)
        st.caption(f"Index: {markov:.2f}")

    if p1 > 0.60 and markov > 0.50:
        st.success("VERDICT: STRONG HOME DOMINANCE")
    elif o25 > 0.70:
        st.success("VERDICT: HIGH SCORE EXPECTED")
