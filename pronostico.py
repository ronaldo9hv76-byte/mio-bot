import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="Lotto Quant Analyser - TXT Mode", layout="wide")

st.title("🎯 Lotto Quant Predictor (Analisi da Archivio TXT)")

def load_data_from_txt():
    # Cerca file .txt nella cartella
    txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]
    
    if not txt_files:
        st.warning("Nessun file .txt trovato nella cartella. Caricalo qui:")
        uploaded_file = st.file_uploader("Carica il file TXT delle estrazioni", type="txt")
        if uploaded_file:
            return process_txt(uploaded_file)
        return None
    
    return process_txt(txt_files[0])

def process_txt(file):
    try:
        # Tenta di leggere il file provando diversi separatori comuni
        # Spazi, Tabulazioni o Virgole
        df = pd.read_csv(file, sep=r'\s+|,|;', engine='python', header=None)
        
        # Rinominiamo le colonne per l'analisi
        # Di solito i file txt hanno: Data, Ruota, N1, N2, N3, N4, N5
        # Se il tuo file ha un formato diverso, adattiamo qui:
        if df.shape[1] >= 7:
            df.columns = ['DATA', 'RUOTA'] + [f'N{i}' for i in range(1, df.shape[1]-1)]
        else:
            st.error("Il formato del file TXT non sembra contenere abbastanza colonne.")
            return None
            
        df['RUOTA'] = df['RUOTA'].astype(str).str.upper()
        return df
    except Exception as e:
        st.error(f"Errore nella lettura del file TXT: {e}")
        return None

# --- ESECUZIONE APP ---
df = load_data_from_txt()

if df is not None:
    st.sidebar.success("✅ Archivio TXT caricato")
    
    ruote = df['RUOTA'].unique()
    ruota_sel = st.sidebar.selectbox("Seleziona Ruota", ruote)
    cols_numeri = [c for c in df.columns if c.startswith('N')][:5]

    def get_esito_expert(data, r_name):
        # Prendiamo solo la ruota scelta e invertiamo l'ordine (più recente in alto)
        df_r = data[data['RUOTA'] == r_name].copy().iloc[::-1].reset_index(drop=True)
        
        results = []
        ritardi_attuali = {}
        
        # 1. Calcolo Ritardo Cronologico (RC)
        for n in range(1, 91):
            # Controlliamo in tutte le colonne N1...N5
            mask = (df_r[cols_numeri] == n).any(axis=1)
            posizioni = df_r.index[mask].tolist()
            ritardi_attuali[n] = posizioni[0] if posizioni else len(df_r)

        # 2. Analisi Sfasamento (Logica Roulette)
        # Analizziamo le ultime 12 estrazioni (60 numeri)
        ultime_estrazioni = df_r.head(12)[cols_numeri].values.flatten()
        alti = len([n for n in ultime_estrazioni if n > 45])
        bassi = len([n for n in ultime_estrazioni if n <= 45])
        
        # Se c'è uno sbilanciamento forte (es: 40 alti su 60 totali)
        bias_bassi = 35 if alti >= 38 else 0
        bias_alti = 35 if bassi >= 38 else 0

        # 3. Calcolo Score
        for n in range(1, 91):
            rc = ritardi_attuali[n]
            score = 0
            
            # Punti Ritardo (Cap a 70 per non esagerare)
            score += min(rc * 0.7, 70) 
            
            # Sfasamento Alti/Bassi
            if n <= 45: score += bias_bassi
            else: score += bias_alti
            
            # Sincronismo (se altri numeri hanno lo stesso ritardo)
            sinc = sum(1 for v in ritardi_attuali.values() if v == rc)
            if sinc > 1: score += 15

            results.append({'Numero': n, 'Score': round(score, 1), 'Ritardo': rc})
            
        return pd.DataFrame(results)

    if st.button("CALCOLA ESITO PROFESSIONALE"):
        res = get_esito_expert(df, ruota_sel)
        # Filtriamo per dare i 3 migliori
        top = res.sort_values('Score', ascending=False).head(3)
        
        st.header(f"📊 Risultato Analisi: {ruota_sel}")
        
        c1, c2, c3 = st.columns(3)
        picks = top.to_dict('records')
        
        for i, col in enumerate([c1, c2, c3]):
            with col:
                st.markdown(f"""
                <div style="background-color:#0e1117; padding:20px; border-radius:15px; border: 2px solid #00ff00; text-align:center;">
                    <h2 style="color:white;">NUMERO</h2>
                    <h1 style="color:#00ff00; font-size:70px; margin:0;">{picks[i]['Numero']}</h1>
                    <p style="font-size:20px;">Score: {picks[i]['Score']}</p>
                    <p style="color:#888;">Ritardo: {picks[i]['Ritardo']}</p>
                </div>
                """, unsafe_allow_html=True)

        st.info("💡 Il programma ha applicato il filtro 'Sfasamento Roulette'. Se vedi uno score alto, il numero è in una fase di forte compensazione statistica.")
