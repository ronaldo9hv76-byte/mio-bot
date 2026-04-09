import streamlit as st
import streamlit.components.v1 as components
import random
import datetime

# Configurazione Dashboard
st.set_page_config(page_title="Payload Control Center", page_icon="💀", layout="wide")

# CSS Custom per un look da Terminale Professionale
st.markdown("""
    <style>
    .main { background-color: #050505; color: #00FF41; font-family: 'Courier New', monospace; }
    .stButton>button { 
        background-color: #1a1a1a; 
        color: #00FF41; 
        border: 1px solid #00FF41; 
        border-radius: 0px;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #00FF41; color: black; box-shadow: 0 0 10px #00FF41; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def generate_tilt_payload():
    # Mix di caratteri invisibili e di controllo per saturare il rendering
    chaos_chars = ["\u202e", "\u202d", "\u2066", "\u2067", "\u1160", "\u3164", "\uFFA0"]
    prefix = "⚠️ [FATAL_ERROR_NODE_7] "
    # Payload massiccio (circa 5000 caratteri)
    payload = prefix + "".join(random.choice(chaos_chars) for _ in range(5000))
    return payload

st.title("📟 TIKTOK_TILT_GENERATOR v2.1")
st.write(f"USER_AUTH: ADMIN | STATUS: ONLINE | {datetime.datetime.now().strftime('%H:%M:%S')}")
st.write("---")

# Sezione Generazione
if st.button("EXECUTE: GENERATE NEW PAYLOAD"):
    st.session_state.payload = generate_tilt_payload()
    st.success("Payload generato e pronto per il deployment.")

# Sezione Output e Copia Automatica
if 'payload' in st.session_state:
    # Mostriamo un'anteprima (anche se sarà quasi vuota dopo il prefisso)
    st.text_area("Payload Preview:", value=st.session_state.payload, height=150, disabled=True)
    
    # --- COMPONENTE JAVASCRIPT PER LA COPIA AUTOMATICA ---
    # Creiamo un tasto HTML/JS personalizzato che interagisce con la clipboard dell'OS
    payload_escaped = st.session_state.payload.replace('"', '\\"') # Escape per JS
    
    copy_button_html = f"""
    <div id="container" style="display: flex; justify-content: center; padding-top: 10px;">
        <button id="copyBtn" style="
            background-color: #00FF41; 
            color: black; 
            border: none; 
            padding: 15px 30px; 
            font-family: 'Courier New', monospace; 
            font-weight: bold; 
            cursor: pointer;
            width: 100%;
        ">
            CLICK TO COPY PAYLOAD TO CLIPBOARD
        </button>
    </div>

    <script>
    const btn = document.getElementById('copyBtn');
    btn.addEventListener('click', function() {{
        const text = "{payload_escaped}";
        navigator.clipboard.writeText(text).then(function() {{
            btn.innerText = "✅ COPIED TO CLIPBOARD!";
            btn.style.backgroundColor = "#FFFFFF";
            setTimeout(() => {{ 
                btn.innerText = "CLICK TO COPY PAYLOAD TO CLIPBOARD"; 
                btn.style.backgroundColor = "#00FF41";
            }}, 2000);
        }}, function(err) {{
            console.error('Errore durante la copia: ', err);
        }});
    }});
    </script>
    """
    
    # Iniettiamo il componente JS nel sito Streamlit
    components.html(copy_button_html, height=100)

st.write("---")
st.caption("Uso consigliato: Genera -> Copia -> Incolla nella Live -> Chiudi la chat.")
