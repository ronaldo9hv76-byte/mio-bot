import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import cv2
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

# Configurazione Pagina Stile Nero Registro
st.set_page_config(page_title="GOTHIC ORACLE v14.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #FF4500; }
    .stButton>button { background-color: #FF4500; color: black; font-weight: bold; width: 100%; }
    .stMetric { background-color: #1A1A1A; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE OCR ---
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

def process_image(uploaded_file):
    image = Image.open(uploaded_file)
    img_array = np.array(image)
    # Conversione per OpenCV e pulizia immagine
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    results = reader.readtext(binary)
    
    nums = []
    for (bbox, text, prob) in results:
        clean = ''.join(filter(str.isdigit, text))
        if clean:
            n = int(clean)
            if 0 <= n <= 36: nums.append(n)
    return nums

# --- LOGICA ESPERTA (Tua Strategia) ---
def analyze_logic(nums):
    analysis = {"alerts": [], "stats": {}}
    if not nums: return analysis
    
    # 1. Sfasamento Alti/Bassi (>18 vs <10)
    last_15 = nums[:15]
    highs = len([n for n in last_15 if n > 18])
    if highs >= 8:
        analysis["alerts"].append(f"🚨 SFASAMENTO RILEVATO: {highs}/15 numeri ALTI. Punta BASSI (<10)!")
    
    # 2. Pattern 50/50 (Pari/Dispari)
    if len(nums) >= 4:
        p_d = ["P" if n % 2 == 0 and n != 0 else "D" for n in nums[:4]]
        if p_d[0] == p_d[1] and p_d[2] == p_d[3] and p_d[1] != p_d[2]:
            analysis["alerts"].append(f"🔄 PATTERN SPECCHIO: {p_d[0]}{p_d[1]}-{p_d[2]}{p_d[3]} rilevato.")

    # 3. Lo Zero e il Freddo
    zero_dist = next((i for i, n in enumerate(nums) if n == 0), 500)
    if zero_dist > 36:
        analysis["alerts"].append(f"❄️ ZERO ASSENTE DA {zero_dist} GIRI. Valuta inserimento.")

    analysis["stats"] = {
        "Ultimo": nums[0],
        "Zero Ritardo": zero_dist,
        "Rapporto R/N": f"{len([n for n in nums if n in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]])}/{len(nums)}"
    }
    return analysis

# --- INTERFACCIA UTENTE ---
st.title("⚡ GOTHIC LIGHTNING v14.0 - ADMIRAL REGISTRY")
st.sidebar.header("CONFIGURAZIONE SESSIONE")
budget = st.sidebar.number_input("Budget Iniziale (€)", value=100)

uploaded_file = st.file_uploader("Carica Screenshot Cronologia (200-500 numeri)", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    with st.spinner('Analisi ottica in corso...'):
        numeri = process_image(uploaded_file)
        
    if numeri:
        st.success(f"Analizzati con successo {len(numeri)} numeri.")
        
        # Dashboard Risultati
        res = analyze_logic(numeri)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("ULTIMO USCITO", res["stats"]["ultimo"])
        col2.metric("RITARDO ZERO", res["stats"]["Zero Ritardo"])
        col3.metric("VOLUME DATI", len(numeri))
        
        st.subheader("📋 VERDETTO ORACOLO")
        for alert in res["alerts"]:
            st.warning(alert)
            
        st.subheader("📊 CRONOLOGIA RILEVATA")
        st.write(numeri)
        
        # Esportazione PDF
        if st.button("SCARICA REGISTRO SESSIONE PDF"):
            # Logica semplice creazione PDF qui (omessa per brevità, usa reportlab)
            st.info("Funzione PDF in fase di generazione...")
    else:
        st.error("Nessun numero rilevato. Assicurati che lo screenshot sia nitido.")

else:
    st.info("In attesa dello screenshot di Admiral Bet per iniziare l'analisi.")
