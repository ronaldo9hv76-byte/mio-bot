import streamlit as st
import pandas as pd
import numpy as np
import easyocr
import cv2
from PIL import Image

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="GOTHIC ORACLE v14.7", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #FF4500; }
    h1, h2, h3 { color: #FF4500; font-family: 'Consolas', monospace; }
    .stButton>button { background-color: #FF4500 !important; color: black !important; font-weight: bold !important; border-radius: 5px; }
    .stMetric { background-color: #1A1A1A; border: 1px solid #333; border-radius: 10px; padding: 10px; }
    .cuscinetto-box { background-color: #002200; padding: 20px; border-radius: 10px; border: 2px solid #00FF00; color: #00FF00; font-family: 'Consolas'; margin-bottom: 20px;}
    .attacco-box { background-color: #220000; padding: 20px; border-radius: 10px; border: 2px solid #FF0000; color: #FF4500; font-family: 'Consolas'; margin-bottom: 20px;}
    .numero-evidenziato { background-color: #FF4500; color: black; padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 1.1em; margin: 2px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE MEMORIA ---
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
def get_cuscinetto_roadmap(nums):
    # Analisi frequenze
    counts = pd.Series(nums).value_counts()
    pivot_nums = counts.index[:3].tolist()
    
    rossi = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
    tot_r = len([n for n in nums if n in rossi])
    tot_n = len([n for n in nums if n != 0 and n not in rossi])
    
    colore_base = "ROSSO" if tot_r < tot_n else "NERO"
    
    roadmap = []
    for i in range(1, 9):
        roadmap.append({"Giro": i, "Colore": colore_base, "Pieni": pivot_nums})
    return roadmap

# --- LOGICA 2: ATTACCO (10 GIRI) ---
def get_attacco_roadmap(nums):
    # Analisi Sfasamento
    last_20 = nums[:20]
    highs = len([n for n in last_20 if n > 18])
    
    # Freddi e Zero
    all_possible = set(range(37))
    usciti = set(nums[:60])
    freddi = list(all_possible - usciti)[:3]
    killer_nums = list(set([0] + freddi + [nums[0]]))[:5]
    
    # Determinazione tendenza colore (Mirroring)
    last_4 = ["R" if n in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36] else "N" for n in nums[:4]]
    colore_attacco = "ROSSO" if last_4.count("N") > 2 else "NERO"
    
    roadmap = []
    for i in range(1, 11):
        # Ogni 3 giri suggeriamo una piccola variazione di copertura
        temp_colore = colore_attacco
        if i % 4 == 0: temp_colore = "ZERO / COPERTURA"
        roadmap.append({"Giro": i, "Colore": temp_colore, "Pieni": killer_nums})
    return roadmap

# --- SIDEBAR MENU ---
st.sidebar.title("💎 GOTHIC MENU")
menu = st.sidebar.radio("Sposta la sessione:", ["FASE 1: Accumulo", "FASE 2: Attacco"], index=0)

if st.sidebar.button("🗑️ RESET SESSIONE"):
    st.session_state.storico_base = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write(f"📊 Numeri in memoria: **{len(st.session_state.storico_base)}**")

# ================= SEZIONE FASE 1 =================
if menu == "FASE 1: Accumulo":
    st.title("🛡️ FASE 1: ACQUISIZIONE & CUSCINETTO")
    st.write("In questa fase analizziamo la base statistica del tavolo.")
    
    files = st.file_uploader("Trascina qui 3 o 4 screenshot storici", accept_multiple_files=True, type=['png','jpg','jpeg'])
    
    if files:
        if st.button("GENERA TABELLA CUSCINETTO"):
            with st.spinner("Scansione in corso..."):
                st.session_state.storico_base = process_images(files)
            
            if st.session_state.storico_base:
                roadmap_c = get_cuscinetto_roadmap(st.session_state.storico_base)
                
                st.markdown("<div class='cuscinetto-box'><h3>🎯 ROADMAP CUSCINETTO (8 GIRI)</h3></div>", unsafe_allow_html=True)
                
                # Tabella Roadmap
                df_c = pd.DataFrame(roadmap_c)
                st.table(df_c)
                
                st.success("Esegui questi 8 giri. Quando sei pronto per l'attacco, seleziona 'FASE 2' dal menu a sinistra.")
            else:
                st.error("Errore lettura. Riprova con screen più chiari.")

# ================= SEZIONE FASE 2 =================
elif menu == "FASE 2: Attacco":
    st.title("🔥 FASE 2: ATTACCO KILLER")
    
    if not st.session_state.storico_base:
        st.warning("⚠️ Non ci sono dati in memoria. Torna alla FASE 1 e carica gli screenshot iniziali!")
    else:
        st.write("Carica l'ultimo screenshot aggiornato per calcolare lo sfasamento finale.")
        
        file_up = st.file_uploader("Upload Ultimo Screen", type=['png','jpg','jpeg'])
        
        if file_up:
            if st.button("GENERA TABELLA D'ATTACCO"):
                with st.spinner("Calcolo numeri Killer..."):
                    nuovi = process_images([file_up])
                    totale = nuovi + st.session_state.storico_base # Unione memorie
                    
                    roadmap_a = get_attacco_roadmap(totale)
                    
                    st.markdown("<div class='attacco-box'><h3>⚔️ ROADMAP D'ATTACCO (10 GIRI)</h3></div>", unsafe_allow_html=True)
                    
                    # Mostriamo i suggerimenti giro per giro
                    for item in roadmap_a:
                        with st.container():
                            c1, c2, c3 = st.columns([1, 2, 4])
                            c1.write(f"**GIRO {item['Giro']}**")
                            c2.write(f"🎨 {item['Colore']}")
                            
                            pieni_str = ""
                            for n in item['Pieni']:
                                pieni_str += f"<span class='numero-evidenziato'>{n}</span> "
                            c3.markdown(pieni_str, unsafe_allow_html=True)
                            st.divider()
                    
                    st.error("⚠️ Fine della sessione d'attacco. Se il risultato è raggiunto, chiudi o resetta la sessione.")

