import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import cv2
from PIL import Image

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="GOTHIC ORACLE v14.5", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #FF4500; }
    h1, h2, h3 { color: #FF4500; font-family: 'Consolas', monospace; }
    .stButton>button { background-color: #FF4500; color: black; font-weight: bold; width: 100%; border-radius: 5px; }
    .stButton>button:hover { background-color: #CC3700; color: white; }
    div[data-testid="stMetricValue"] { color: #FF4500; font-size: 2rem; }
    div[data-testid="metric-container"] { background-color: #1A1A1A; padding: 15px; border-radius: 8px; border: 1px solid #333333; }
    .cuscinetto-box { background-color: #003300; padding: 15px; border-radius: 5px; border-left: 5px solid #00FF00; color: #00FF00; font-family: 'Consolas'; margin-bottom: 20px;}
    .attacco-box { background-color: #330000; padding: 15px; border-radius: 5px; border-left: 5px solid #FF0000; color: #FF4500; font-family: 'Consolas'; margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE MEMORIA (Session State) ---
if 'fase' not in st.session_state:
    st.session_state.fase = 1
if 'storico_base' not in st.session_state:
    st.session_state.storico_base = []

# --- MOTORE OCR ---
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

def process_images(uploaded_files):
    all_nums = []
    for file in uploaded_files:
        image = Image.open(file)
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        results = reader.readtext(binary)
        
        file_nums = []
        for (bbox, text, prob) in results:
            clean = ''.join(filter(str.isdigit, text))
            if clean:
                n = int(clean)
                if 0 <= n <= 36: 
                    file_nums.append(n)
        all_nums.extend(file_nums)
    return all_nums

# --- LOGICA CUSCINETTO (Primi 8 Giri) ---
def calcola_cuscinetto(nums):
    rossi_storici = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    tot_rossi = len([n for n in nums if n in rossi_storici])
    tot_neri = len([n for n in nums if n != 0 and n not in rossi_storici])
    
    # Trova lo squilibrio per consigliare le esterne
    suggerimento = "Gioca con puntata MINIMA sulle chance semplici per accumulare bankroll.\n\n"
    if tot_rossi < tot_neri - 5:
        suggerimento += "🎯 STRATEGIA: Punta ROSSO (in leggero ritardo statistico).\n"
    elif tot_neri < tot_rossi - 5:
        suggerimento += "🎯 STRATEGIA: Punta NERO (in leggero ritardo statistico).\n"
    else:
        suggerimento += "🎯 STRATEGIA: Punta DOZZINA 2 (Zona centrale di equilibrio).\n"
        
    suggerimento += "⏳ Esegui questa tecnica per i prossimi 8 GIRI."
    return suggerimento

# --- LOGICA ATTACCO FINALE (I 10 Giri) ---
def calcola_attacco(nums):
    alerts = []
    last_15 = nums[:15] # Assumendo che i primi elementi siano gli ultimi usciti
    
    # 1. Sfasamento Alti/Bassi
    highs = len([n for n in last_15 if n > 18])
    if highs >= 8:
        alerts.append("🚨 SFASAMENTO ESTREMO: Troppi numeri ALTI. Tecnica d'attacco: SETTORE BASSI (<10) + ZERO.")
    elif highs <= 3:
        alerts.append("🚨 SFASAMENTO ESTREMO: Troppi numeri BASSI. Tecnica d'attacco: SETTORE ALTI (>25).")
        
    # 2. Pattern Pari/Dispari
    if len(nums) >= 4:
        p_d = ["P" if n % 2 == 0 and n != 0 else "D" for n in nums[:4]]
        if p_d[0] == p_d[1] and p_d[2] == p_d[3] and p_d[1] != p_d[2]:
            alerts.append(f"🔄 PATTERN SPECCHIO {p_d[0]}{p_d[1]}-{p_d[2]}{p_d[3]}: Punta forte sulla rottura dello schema.")

    # 3. Lo Zero e i Freddi
    zero_dist = next((i for i, n in enumerate(nums) if n == 0), 500)
    if zero_dist > 36:
        alerts.append(f"❄️ ATTACCO ALLO ZERO: Manca da {zero_dist} giri. Includilo fisso per i prossimi 10 giri insieme ai due numeri più freddi della sessione.")
        
    if not alerts:
        alerts.append("⚖️ Nessuna anomalia estrema. Gioca una sessione conservativa: Orfanelli + Zero per 10 giri.")
        
    return alerts

# --- INTERFACCIA UTENTE ---
st.title("⚡ GOTHIC LIGHTNING v14.5 - MULTI-STAGE ANALYSIS")

st.sidebar.header("CONTROLLO SESSIONE")
if st.sidebar.button("🔄 RESETTA SESSIONE (Nuovo Tavolo)"):
    st.session_state.fase = 1
    st.session_state.storico_base = []
    st.rerun()

st.sidebar.markdown(f"**FASE ATTUALE:** {'1 (Cuscinetto)' if st.session_state.fase == 1 else '2 (Attacco)'}")
st.sidebar.markdown(f"**NUMERI IN MEMORIA:** {len(st.session_state.storico_base)}")

# ==========================================
# FASE 1: CARICAMENTO INIZIALE E CUSCINETTO
# ==========================================
if st.session_state.fase == 1:
    st.header("FASE 1: Acquisizione Dati & Cuscinetto")
    st.info("Carica 3 o 4 screenshot storici contemporaneamente per avere un campione statistico ampio.")
    
    # accept_multiple_files=True permette di selezionare più foto assieme
    uploaded_files = st.file_uploader("Seleziona Screen Multipli", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    
    if uploaded_files and len(uploaded_files) > 0:
        if st.button("ANALIZZA SCREENSHOT E CREA CUSCINETTO"):
            with st.spinner('Lettura OCR di massa in corso...'):
                numeri_base = process_images(uploaded_files)
                st.session_state.storico_base = numeri_base
                
            if len(st.session_state.storico_base) > 0:
                st.success(f"Libreria aggiornata: {len(st.session_state.storico_base)} numeri acquisiti in totale.")
                
                cuscinetto_txt = calcola_cuscinetto(st.session_state.storico_base)
                st.markdown(f"<div class='cuscinetto-box'><b>STRATEGIA CUSCINETTO (PROSSIMI 8 GIRI)</b><br><br>{cuscinetto_txt}</div>", unsafe_allow_html=True)
                
                st.warning("⚠️ Gioca i tuoi 8 giri come indicato sopra. Quando hai finito, fai un nuovo screenshot aggiornato e clicca sul pulsante qui sotto.")
                
                if st.button("PASSA ALLA FASE 2: ATTACCO FINALE"):
                    st.session_state.fase = 2
                    st.rerun()
            else:
                st.error("Errore: Nessun numero letto. Verifica la qualità delle immagini.")

# ==========================================
# FASE 2: AGGIORNAMENTO E ATTACCO
# ==========================================
elif st.session_state.fase == 2:
    st.header("FASE 2: Aggiornamento & Attacco (I 10 Giri)")
    st.info("Gli 8 giri di cuscinetto sono terminati. Carica l'ULTIMO screenshot per calcolare l'impatto finale.")
    
    uploaded_update = st.file_uploader("Carica 1 Screen Aggiornato", type=['png', 'jpg', 'jpeg'], accept_multiple_files=False)
    
    if uploaded_update:
        if st.button("CALCOLA ATTACCO"):
            with st.spinner('Integrazione nuovi dati e calcolo algoritmi...'):
                nuovi_numeri = process_images([uploaded_update])
                
                # Uniamo la vecchia memoria con i nuovi dati (mettiamo i nuovi davanti)
                storico_completo = nuovi_numeri + st.session_state.storico_base
                
            st.success(f"Analisi completata. Volume totale: {len(storico_completo)} numeri storici.")
            
            attacchi = calcola_attacco(storico_completo)
            
            st.markdown("<div class='attacco-box'><b>🔥 TECNICA DI ATTACCO (PROSSIMI 10 GIRI)</b></div>", unsafe_allow_html=True)
            for alert in attacchi:
                st.error(alert)
                
            col1, col2 = st.columns(2)
            col1.metric("ZERO ASSENTE DA", next((i for i, n in enumerate(storico_completo) if n == 0), "N/A"))
            col2.metric("ULTIMO NUMERO USCITO", storico_completo[0])

            st.markdown("---")
            st.info("Al termine dei 10 giri, premi 'Resetta Sessione' nella barra laterale per ricominciare da capo su un nuovo tavolo.")
