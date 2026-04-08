import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import cv2
from PIL import Image

# --- CONFIGURAZIONE PAGINA (Stile Nero Registro) ---
st.set_page_config(page_title="GOTHIC ORACLE v14.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #FF4500; }
    h1, h2, h3 { color: #FF4500; font-family: 'Consolas', monospace; }
    .stButton>button { background-color: #FF4500; color: black; font-weight: bold; width: 100%; border-radius: 5px; }
    .stButton>button:hover { background-color: #CC3700; color: white; }
    div[data-testid="stMetricValue"] { color: #FF4500; font-size: 2rem; }
    div[data-testid="metric-container"] { background-color: #1A1A1A; padding: 15px; border-radius: 8px; border: 1px solid #333333; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE OCR (Lettura Immagini) ---
@st.cache_resource
def load_ocr():
    # Cache per non ricaricare il modello ad ogni click
    return easyocr.Reader(['en'])

reader = load_ocr()

def process_image(uploaded_file):
    image = Image.open(uploaded_file)
    img_array = np.array(image)
    
    # Pre-processing OpenCV: Convertiamo in scala di grigi e aumentiamo il contrasto
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    # OCR elabora l'immagine
    results = reader.readtext(binary)
    
    nums = []
    for (bbox, text, prob) in results:
        # Estraiamo solo i numeri interi tra 0 e 36
        clean = ''.join(filter(str.isdigit, text))
        if clean:
            n = int(clean)
            if 0 <= n <= 36: 
                nums.append(n)
    return nums

# --- LOGICA ESPERTA (La tua Strategia 10 Anni) ---
def analyze_logic(nums):
    analysis = {"alerts": [], "stats": {}}
    if not nums: return analysis
    
    # 1. Sfasamento Alti/Bassi (>18 vs <10)
    last_15 = nums[:15]
    highs = len([n for n in last_15 if n > 18])
    if highs >= 8:
        analysis["alerts"].append(f"🚨 SFASAMENTO RILEVATO: {highs}/15 numeri ALTI. Punta BASSI (<10)!")
    
    # 2. Pattern 50/50 (Pari/Dispari Speculare)
    if len(nums) >= 4:
        p_d = ["P" if n % 2 == 0 and n != 0 else "D" for n in nums[:4]]
        if p_d[0] == p_d[1] and p_d[2] == p_d[3] and p_d[1] != p_d[2]:
            analysis["alerts"].append(f"🔄 PATTERN SPECCHIO: {p_d[0]}{p_d[1]}-{p_d[2]}{p_d[3]} rilevato. Valuta ripetizione o rottura.")

    # 3. Lo Zero e i Freddi
    zero_dist = next((i for i, n in enumerate(nums) if n == 0), 500)
    if zero_dist > 36:
        analysis["alerts"].append(f"❄️ ZERO ASSENTE DA {zero_dist} GIRI. Momento critico: inizia copertura.")

    # Salvataggio Statistiche sicure
    rossi_storici = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    tot_rossi = len([n for n in nums if n in rossi_storici])
    
    analysis["stats"] = {
        "Ultimo": nums[0],
        "Zero Ritardo": zero_dist if zero_dist != 500 else "Non Rilevato",
        "Rapporto R/N": f"{tot_rossi}/{len(nums)}"
    }
    return analysis

# --- INTERFACCIA UTENTE (Dashboard) ---
st.title("⚡ GOTHIC LIGHTNING v14.0 - ADMIRAL VISION")

# Sidebar
st.sidebar.header("CONFIGURAZIONE SESSIONE")
budget = st.sidebar.number_input("Bankroll Iniziale (€)", value=100)
st.sidebar.markdown("---")
st.sidebar.info("💡 Fai lo screenshot della cronologia dei numeri su Admiral Bet e caricalo qui a fianco. Più la foto è ritagliata sui numeri, più precisa sarà la lettura.")

# Caricamento File
uploaded_file = st.file_uploader("CARICA SCREENSHOT CRONOLOGIA (Formato orizzontale o griglia)", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    with st.spinner('Scansione ottica e ricerca pattern in corso...'):
        numeri = process_image(uploaded_file)
        
    if numeri:
        st.success(f"Dati acquisiti: elaborati {len(numeri)} numeri.")
        
        # Elaborazione risultati
        res = analyze_logic(numeri)
        stats = res.get("stats", {})
        
        # Metriche principali
        col1, col2, col3 = st.columns(3)
        col1.metric("ULTIMO USCITO", stats.get("Ultimo", "N/A"))
        col2.metric("RITARDO ZERO", stats.get("Zero Ritardo", "N/A"))
        col3.metric("NUMERI PROCESSATI", len(numeri))
        
        # Area Verdetto
        st.subheader("📋 VERDETTO ORACOLO")
        if res["alerts"]:
            for alert in res["alerts"]:
                st.warning(alert)
        else:
            st.info("⚖️ Nessuno sfasamento grave rilevato. La roulette è in equilibrio. Consigliata fase di CUSCINETTO (Puntate esterne minime).")
            
        # Storico grezzo
        with st.expander("Vedi Cronologia Grezza Rilevata"):
            st.write(numeri)
            
    else:
        st.error("❌ Nessun numero rilevato dall'immagine. Assicurati che lo screenshot sia nitido e che mostri chiaramente i numeri in contrasto con lo sfondo.")

else:
    st.info("⚡ In attesa dello screenshot. Il sistema è pronto.")
