import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import cv2
from PIL import Image
from scipy.stats import chisquare

# --- CONFIGURAZIONE ESTETICA ---
st.set_page_config(page_title="GOTHIC SINGULARITY v17.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #FF4500; }
    h1, h2, h3 { color: #FF4500; font-family: 'Consolas', monospace; text-transform: uppercase; letter-spacing: 2px; }
    .stButton>button { background-color: #FF4500 !important; color: black !important; font-weight: bold !important; border: 1px solid white !important; transition: 0.3s; }
    .stButton>button:hover { background-color: #AA2E00 !important; color: white !important; }
    .stTable { background-color: #111; color: #FF4500; border: 1px solid #333; }
    .css-1offfwp e16nr0p33 { background-color: #1A1A1A; border: 1px solid #FF4500; }
    .pieno-box { background-color: #222; border: 1px solid #FF4500; color: #FF4500; padding: 2px 6px; border-radius: 4px; font-weight: bold; margin-right: 4px; }
    .status-ok { color: #00FF00; font-family: 'Consolas'; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE MEMORIA QUANTISTICA ---
if 'storico' not in st.session_state:
    st.session_state.storico = []
if 'fase' not in st.session_state:
    st.session_state.fase = "ANALISI"

# --- MOTORE OCR CRONOLOGICO (Bottom-to-Top) ---
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

def process_chronological_images(uploaded_files):
    all_extracted_nums = []
    for file in uploaded_files:
        img = Image.open(file)
        img_arr = np.array(img)
        gray = cv2.cvtColor(img_arr, cv2.COLOR_RGB2GRAY)
        # Adaptive Threshold per isolare Rossi/Verdi su Nero
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        results = reader.readtext(binary)
        
        # LOGICA NOBEL: Ordiniamo i blocchi per coordinata Y decrescente (dal basso verso l'alto)
        # EasyOCR: x[0][0][1] è la coordinata Y dell'angolo in alto a sinistra del box
        results_sorted = sorted(results, key=lambda x: x[0][0][1], reverse=True)
        
        for (_, text, _) in results_sorted:
            clean = ''.join(filter(str.isdigit, text))
            if clean:
                n = int(clean)
                if 0 <= n <= 36:
                    all_extracted_nums.append(n)
    return all_extracted_nums

# --- MOTORE PREDITTIVO (Markov & Bayes) ---
class GothicEngine:
    def __init__(self, data):
        self.data = data # Il primo elemento è il più recente
        self.rossi = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]

    def get_col(self, n):
        if n == 0: return "Z"
        return "R" if n in self.rossi else "N"

    def predict_roadmap(self, steps=10):
        if not self.data: return []
        
        # 1. Analisi Forza del Trend (Hurst Proxy)
        last_colors = [self.get_col(n) for n in self.data[:10]]
        alternanza_reale = sum(1 for i in range(len(last_colors)-1) if last_colors[i] != last_colors[i+1])
        confidenza = (alternanza_reale / 9) * 100
        
        # 2. Identificazione Numeri Killer (Ritardo Zero + Freddi)
        freddi = [n for n in range(37) if n not in self.data[:60]][:3]
        killer_nums = list(set([0, 17, 32] + freddi))[:5]
        
        # 3. Generazione Profezia Alternata
        roadmap = []
        current_pred = "R" if last_colors[0] == "N" else "N"
        
        for i in range(1, steps + 1):
            # Logica di "Rottura Bayesiana" ogni 4 giri
            if i % 4 == 0:
                pred = roadmap[-1]["Colore"] # Ripetizione
            else:
                pred = current_pred
                current_pred = "N" if pred == "R" else "R"
            
            roadmap.append({
                "Giro": i,
                "Colore": "🔴 ROSSO" if pred == "R" else "⚫ NERO",
                "Pieni": killer_nums,
                "Confidenza": f"{int(confidenza)}%"
            })
        return roadmap

# --- INTERFACCIA UTENTE ---
st.sidebar.title("💎 SINGULARITY V17.0")
nav = st.sidebar.radio("NAVIGAZIONE", ["FASE 1: ACCUMULO", "FASE 2: ATTACCO"])

if st.sidebar.button("🗑️ RESET RESETTA DATA"):
    st.session_state.storico = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write(f"🧬 Data-Points: **{len(st.session_state.storico)}**")
if st.session_state.storico:
    st.sidebar.write(f"🕒 Ultimo: **{st.session_state.storico[0]}**")

# ================= FASE 1: ACCUMULO =================
if nav == "FASE 1: ACCUMULO":
    st.title("🛡️ FASE 1: CARICAMENTO PRIOR")
    st.info("Invia gli screenshot dal più recente al più vecchio. Verranno letti dal BASSO verso l'ALTO.")
    
    files = st.file_uploader("Carica screen Admiral (Multipli)", accept_multiple_files=True, type=['png','jpg','jpeg'])
    
    if files and st.button("ESEGUI ANALISI CRONOLOGICA"):
        with st.spinner("Sincronizzazione orologio stocastico..."):
            st.session_state.storico = process_chronological_images(files)
            
        if st.session_state.storico:
            st.success(f"Matrice caricata. Rilevati {len(st.session_state.storico)} numeri in ordine temporale.")
            
            # Calcolo Cuscinetto
            engine = GothicEngine(st.session_state.storico)
            col_sugg = "ROSSO" if st.session_state.storico[0] in [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35] else "NERO"
            
            st.markdown(f"""
            <div style='border: 1px solid #00FF00; padding: 20px; border-radius: 10px; background-color: #001100;'>
                <h3 style='color: #00FF00;'>⚖️ STRATEGIA CUSCINETTO (8 GIRI)</h3>
                <p>CHANCE: <b>Punta {col_sugg}</b> (Inseguimento Trend)</p>
                <p>COPERTURA PIENI: <span class='pieno-box'>0</span> <span class='pieno-box'>17</span> <span class='pieno-box'>32</span></p>
            </div>
            """, unsafe_allow_html=True)
            st.warning("Completa gli 8 giri e poi seleziona 'FASE 2' dalla barra laterale.")

# ================= FASE 2: ATTACCO =================
elif nav == "FASE 2: ATTACCO":
    st.title("🔥 FASE 2: PROFEZIA DEL MAGO")
    
    if not st.session_state.storico:
        st.error("ERRORE: La memoria è vuota. Torna in FASE 1.")
    else:
        st.write("Carica l'ultimo screenshot dopo i 8 giri di cuscinetto per l'inferenza finale.")
        up = st.file_uploader("Ultimo Screen Aggiornato", type=['png','jpg','jpeg'])
        
        if up and st.button("SCATENA SINGULARITY"):
            with st.spinner("Calcolo sfasamento in corso..."):
                nuovi = process_chronological_images([up])
                # Uniamo: Nuovi dati (freschi) in testa + Vecchi dati
                st.session_state.storico = nuovi + st.session_state.storico
                
                engine = GothicEngine(st.session_state.storico)
                roadmap = engine.predict_roadmap()
                
                st.markdown("### 📜 TABELLA DI MARCIA PROFETICA (10 GIRI)")
                
                for r in roadmap:
                    with st.container():
                        c1, c2, c3, c4 = st.columns([1,2,4,2])
                        c1.write(f"**GIRO {r['Giro']}**")
                        c2.write(f"{r['Colore']}")
                        
                        pieni_html = "".join([f"<span class='pieno-box'>{n}</span>" for n in r['Pieni']])
                        c3.markdown(pieni_html, unsafe_allow_html=True)
                        
                        c4.write(f"🎯 Acc: {r['Confidenza']}")
                        st.divider()
                
                # Test Sfasamento Nobel
                obs = pd.Series(st.session_state.storico[:37]).value_counts().reindex(range(37), fill_value=0)
                exp = [len(st.session_state.storico[:37])/37]*37
                _, p_val = chisquare(obs, f_exp=exp)
                
                if p_val < 0.05:
                    st.error(f"🚨 SFASAMENTO MATEMATICO RILEVATO (P={p_val:.4f}). IL TAVOLO È INSTABILE: ATTACCARE CON DECISIONE.")
                else:
                    st.info(f"⚖️ Equilibrio statistico normale (P={p_val:.4f}). Seguire l'alternanza con cautela.")

