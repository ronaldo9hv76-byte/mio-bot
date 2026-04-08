import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import cv2
from PIL import Image
from scipy.stats import chisquare

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="GOTHIC SINGULARITY v17.2", layout="wide")

# --- CSS ---
st.markdown("""
    <style>
    .main { background-color: #000; color: #FF4500; }
    .stButton>button { width: 100%; background-color: #FF4500 !important; color: black !important; font-weight: bold; }
    .pieno-box { background-color: #222; border: 1px solid #FF4500; color: #FF4500; padding: 2px 8px; border-radius: 4px; margin-right: 5px; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- MEMORIA ---
if 'storico' not in st.session_state:
    st.session_state.storico = []

# --- MOTORE OCR (CON ORDINE CRONOLOGICO) ---
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

def process_images_safe(uploaded_files):
    all_nums = []
    if not uploaded_files:
        return []
    
    for file in uploaded_files:
        try:
            image = Image.open(file)
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            results = reader.readtext(binary)
            # Ordine dal basso verso l'alto (Y decrescente)
            results_sorted = sorted(results, key=lambda x: x[0][0][1], reverse=True)
            
            for (_, text, _) in results_sorted:
                clean = ''.join(filter(str.isdigit, text))
                if clean:
                    n = int(clean)
                    if 0 <= n <= 36:
                        all_nums.append(n)
        except Exception as e:
            st.error(f"Errore nella lettura di un file: {e}")
            continue
    return all_nums

# --- MOTORE NOBEL ---
class NobelWizard:
    def __init__(self, data):
        self.data = data
        self.rossi = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]

    def predict(self):
        if len(self.data) < 2: return []
        
        # Numeri Killer (Zero + Freddi)
        freddi = [n for n in range(37) if n not in self.data[:50]][:3]
        killer = list(set([0, 17, 32] + freddi))[:5]
        
        # Alternanza Mago
        last_col = "R" if self.data[0] in self.rossi else "N"
        roadmap = []
        next_pred = "N" if last_col == "R" else "R"
        
        for i in range(1, 11):
            # Ogni 4 colpi il Mago prevede la rottura (ripetizione)
            if i % 4 == 0:
                final_col = "🔴 R" if next_pred == "N" else "⚫ N" # Inverte la predizione per ripetere l'ultimo
            else:
                final_col = "🔴 ROSSO" if next_pred == "R" else "⚫ NERO"
                next_pred = "N" if next_pred == "R" else "R"
            
            roadmap.append({"Giro": i, "Puntata": final_col, "Pieni": killer})
        return roadmap

# --- INTERFACCIA ---
st.sidebar.title("🔮 GOTHIC ORACOLO")
fase = st.sidebar.radio("Scegli Fase:", ["1. ACCUMULO (Cuscinetto)", "2. PROFEZIA (Attacco)"])

if st.sidebar.button("🗑️ RESET"):
    st.session_state.storico = []
    st.rerun()

# FASE 1
if fase == "1. ACCUMULO (Cuscinetto)":
    st.title("🛡️ FASE 1: ANALISI CRONOLOGICA")
    files = st.file_uploader("Carica screen (Ordine: Recente -> Vecchio)", accept_multiple_files=True)
    
    if files and st.button("ESEGUI ANALISI"):
        nums = process_images_safe(files)
        if nums:
            st.session_state.storico = nums
            st.success(f"Analizzati {len(nums)} numeri dal basso verso l'alto.")
            
            # Consiglio Cuscinetto Rapido
            ultimo = st.session_state.storico[0]
            col = "ROSSO" if ultimo in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36] else "NERO"
            st.info(f"🎯 GIOCA CUSCINETTO (8 giri): Punta {col} e copri lo ZERO.")
        else:
            st.error("Nessun numero rilevato. Controlla la qualità delle foto.")

# FASE 2
else:
    st.title("🔥 FASE 2: PROFEZIA DEI 10 GIRI")
    if not st.session_state.storico:
        st.warning("Torna in Fase 1 per caricare i dati.")
    else:
        file_up = st.file_uploader("Carica l'ultimo screen aggiornato")
        if file_up and st.button("GENERA PROFEZIA"):
            nuovi = process_images_safe([file_up])
            if nuovi:
                # Unione intelligente
                st.session_state.storico = nuovi + st.session_state.storico
                wizard = NobelWizard(st.session_state.storico)
                roadmap = wizard.predict()
                
                st.subheader("📜 TABELLA DI MARCIA")
                for r in roadmap:
                    col1, col2, col3 = st.columns([1,2,4])
                    col1.write(f"**Giro {r['Giro']}**")
                    col2.write(f"{r['Puntata']}")
                    pieni_str = "".join([f"<span class='pieno-box'>{n}</span>" for n in r['Pieni']])
                    col3.markdown(pieni_html := pieni_str, unsafe_allow_html=True)
                    st.divider()
            else:
                st.error("Errore lettura ultimo screen.")
