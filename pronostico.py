import streamlit as st
import random
import datetime

st.set_page_config(page_title="UI Stress Tester", page_icon="📈", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stButton>button { border-radius: 8px; height: 3em; width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def generate_heavy_load_string():
    # Caratteri che richiedono un rendering multi-layer (Emoji complesse + Simboli rari)
    # Questi forzano il sistema a caricare diversi set di font contemporaneamente
    assets = ["💠", "🌀", "🧿", "🛰️", "🧬", "🧪", "🧫", "📡", "🦾", "⚡", "ꖘ", "𐫰", "𒀱", "𒈓"]
    
    # Prefisso per identificare il test
    prefix = f"[TEST_LOAD_{random.randint(100,999)}] "
    
    # TikTok limite ~150 caratteri. Usiamo 145 per sicurezza.
    test_string = prefix
    while len(test_string) < 145:
        test_string += random.choice(assets)
    
    return test_string

st.title("📈 UI Buffer Stress Tester")
st.write("Strumento per la valutazione della fluidità del rendering in ambienti Live.")

if st.button("GENERARE NUOVO PACCHETTO DATI"):
    st.session_state.test_payload = generate_heavy_load_string()

if 'test_payload' in st.session_state:
    st.text_area("Stringa Generata (Standard Load):", value=st.session_state.test_payload, height=100)
    
    # Tasto di copia rapida per lo spamming manuale
    # Nota: su mobile, navigator.clipboard richiede connessione HTTPS
    payload_escaped = st.session_state.test_payload.replace('"', '\\"')
    copy_js = f"""
    <button onclick="copyToClipboard()" style="width:100%; height:50px; background-color:#ff4b4b; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">
        COPIA E PREPARA PER INVIO RAPIDO
    </button>

    <script>
    function copyToClipboard() {{
        const el = document.createElement('textarea');
        el.value = "{payload_escaped}";
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        alert('Stringa Copiata. Incollala ripetutamente nella Live.');
    }}
    </script>
    """
    st.components.v1.html(copy_js, height=80)

st.info("**Protocollo di Test:** Per valutare il lag, invia la stringa copiata 5-10 volte in rapida successione. Monitora il calo di FPS (Frame Per Second) sul dispositivo che riceve i messaggi.")
