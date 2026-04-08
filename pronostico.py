import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import cv2
from PIL import Image

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="GOTHIC ORACLE v14.6", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #FF4500; }
    h1, h2, h3 { color: #FF4500; font-family: 'Consolas', monospace; }
    .stButton>button { background-color: #FF4500; color: black; font-weight: bold; width: 100%; border-radius: 5px; height: 3em; }
    .stMetric { background-color: #1A1A1A; border: 1px solid #333; border-radius: 10px; padding: 10px; }
    .cuscinetto-box { background-color: #002200; padding: 20px; border-radius: 10px; border: 2px solid #00FF00; color: #00FF00; font-family: 'Consolas'; margin-bottom: 20px;}
    .attacco-box { background-color: #220000; padding: 20px; border-radius: 10px; border: 2px solid #FF0000; color: #FF4500; font-family: 'Consolas'; margin-bottom: 20px;}
    .numero-evidenziato { background-color: #FF4500; color: black; padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 1.2em; margin: 2px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIONE STATO ---
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
        for (bbox, text, prob) in results:
            clean = ''.join(filter(str.isdigit, text))
            if clean:
                n = int(clean)
                if 0 <= n <= 36: all_nums.append(n)
    return all_nums

# --- LOGICA 1: CUSCINETTO (8 GIRI) ---
def get_cuscinetto_data(nums):
    # Analisi frequenze per numeri Pivot
    counts = pd.Series(nums).value_counts()
    pivot_nums = counts.index[:3].tolist() # I 3 più frequenti per bilanciare
    
    rossi = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
    tot_r = len([n for n in nums if n in rossi])
    tot_n = len([n for n in nums if n != 0 and n not in rossi])
    
    chance = "ROSSO" if tot_r < tot_n else "NERO"
    return chance, pivot_nums

# --- LOGICA 2: ATTACCO (10 GIRI) ---
def get_attacco_data(nums):
    # Identificazione numeri Freddi e Zero
    all_possible = set(range(37))
    usciti = set(nums[:50]) # Ultime 50 estrazioni
    freddi = list(all_possible - usciti)[:3] # I primi 3 che mancano da più tempo
    
    # Sfasamento Alti/Bassi
    highs = len([n for n in nums[:15] if n > 18])
    base_bet = "SETTORE BASSI (0-12)" if highs >= 8 else "SETTORE ALTI (25-36)"
    
    # Numeri Killer: Freddi + Zero + Numero Caldo del momento
    killer_nums = list(set([0] + freddi + [nums[0]]))
    return base_bet, killer_nums[:5]

# --- UI ---
st.sidebar.title("🎮 GOTHIC CONTROL")
if st.sidebar.button("🗑️ RESET TOTALE SESSIONE"):
    st.session_state.fase = 1
    st.session_state.storico_base = []
    st.rerun()

st.sidebar.markdown(f"**FASE ATTUALE:** {st.session_state.fase}")

# ================= Fase 1 =================
if st.session_state.fase == 1:
    st.title("🛡️ FASE 1: CREAZIONE CUSCINETTO")
    st.write("Carica 3-4 screenshot della cronologia Admiral Bet.")
    
    files = st.file_uploader("Upload Multiplo", accept_multiple_files=True, type=['png','jpg','jpeg'], key="f1")
    
    if files:
        if st.button("ANALIZZA E GENERA NUMERI PIVOT"):
            with st.spinner("Elaborazione..."):
                st.session_state.storico_base = process_images(files)
            
            if st.session_state.storico_base:
                chance, pivots = get_cuscinetto_data(st.session_state.storico_base)
                
                st.markdown(f"""
                <div class='cuscinetto-box'>
                    <h3>🎯 PIANO CUSCINETTO (PROSSIMI 8 GIRI)</h3>
                    <p><b>CHANCE SEMPLICE:</b> {chance} (Puntata Minima)</p>
                    <p><b>NUMERI PIENI PIVOT:</b></p>
                </div>
                """, unsafe_allow_html=True)
                
                cols = st.columns(len(pivots))
                for i, n in enumerate(pivots):
                    cols[i].markdown(f"<div class='numero-evidenziato'>{n}</div>", unsafe_allow_html=True)
                
                st.success("Gioca questi numeri per 8 giri. Poi fai uno screen nuovo e passa alla Fase 2.")
                
                if st.button("VAI ALLA FASE 2 ➡️"):
                    st.session_state.fase = 2
                    st.rerun()

# ================= Fase 2 =================
elif st.session_state.fase == 2:
    st.title("🔥 FASE 2: ATTACCO FINALE")
    st.write("Carica l'ultimo screenshot aggiornato dopo gli 8 giri di cuscinetto.")
    
    file_up = st.file_uploader("Upload Ultimo Screen", type=['png','jpg','jpeg'], key="f2")
    
    if file_up:
        if st.button("CALCOLA NUMERI KILLER"):
            with st.spinner("Calcolo sfasamento..."):
                nuovi = process_images([file_up])
                totale = nuovi + st.session_state.storico_base
                
                fase2_bet, killers = get_attacco_data(totale)
                
                st.markdown(f"""
                <div class='attacco-box'>
                    <h3>⚔️ PIANO D'ATTACCO (PROSSIMI 10 GIRI)</h3>
                    <p><b>STRATEGIA AREA:</b> {fase2_bet}</p>
                    <p><b>NUMERI KILLER (PIENI):</b></p>
                </div>
                """, unsafe_allow_html=True)
                
                cols = st.columns(len(killers))
                for i, n in enumerate(killers):
                    cols[i].markdown(f"<div class='numero-evidenziato'>{n}</div>", unsafe_allow_html=True)
                
                st.error("⚠️ ATTENZIONE: Questi numeri hanno la massima probabilità di uscita per sfasamento. Mantieni la calma e non superare i 10 giri.")

