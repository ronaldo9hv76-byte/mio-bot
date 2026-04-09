import streamlit as st
import pandas as pd
import numpy as np
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Lotto Quant Analyser - Expert", layout="wide")

# Mappa per i nomi completi delle ruote
MAPPA_RUOTE = {
    'BA': 'Bari', 'CA': 'Cagliari', 'FI': 'Firenze', 'GE': 'Genova',
    'MI': 'Milano', 'NA': 'Napoli', 'PA': 'Palermo', 'RM': 'Roma',
    'RN': 'Nazionale', 'TO': 'Torino', 'VE': 'Venezia'
}

st.title("🎯 Lotto Quant Predictor")
st.write("Analisi Professionale: Sfasamento Statistico e Ritardi")

# --- CARICAMENTO DATI FORZATO ---
@st.cache_data
def load_data():
    file_target = 'storico.txt'
    
    # Controlla se il file esiste fisicamente
    if not os.path.exists(file_target):
        st.error(f"❌ File '{file_target}' non trovato nella cartella! Crealo e inserisci le estrazioni.")
        return None

    try:
        # Legge il file ignorando gli spazi multipli
        df = pd.read_csv(file_target, sep=r'\s+', header=None, engine='python')
        # Forza i nomi delle colonne in base al tuo screenshot
        df.columns = ['DATA', 'SIGLA', 'N1', 'N2', 'N3', 'N4', 'N5']
        return df
    except Exception as e:
        st.error(f"❌ Errore nella lettura del file: {e}")
        return None

# Carica il dataframe
df = load_data()

# --- LOGICA DEL PROGRAMMA ---
if df is not None:
    st.sidebar.success("✅ File 'storico.txt' letto con successo!")
    
    # Crea il menu a tendina con i nomi interi delle ruote
    sigle_disponibili = df['SIGLA'].unique()
    opzioni_ruota = {MAPPA_RUOTE.get(s, s): s for s in sigle_disponibili}
    scelta_nome = st.sidebar.selectbox("Seleziona Ruota", list(opzioni_ruota.keys()))
    sigla_sel = opzioni_ruota[scelta_nome]

    def analizza_esito(data, sigla):
        # Filtra per ruota, inverte l'ordine (ultima estrazione in cima) e resetta l'indice
        df_r = data[data['SIGLA'] == sigla].copy().iloc[::-1].reset_index(drop=True)
        cols_n = ['N1', 'N2', 'N3', 'N4', 'N5']
        
        # 1. Calcolo dei Ritardi Cronologici (RC)
        ritardi = {}
        for n in range(1, 91):
            mask = (df_r[cols_n] == n).any(axis=1)
            ritardi[n] = df_r.index[mask][0] if mask.any() else len(df_r)

        # 2. Analisi Sfasamento (Logica "Roulette" Alti vs Bassi)
        # Prendiamo le ultime 12 estrazioni (60 numeri)
        pool_recenti = df_r.head(12)[cols_n].values.flatten()
        alti = len([n for n in pool_recenti if n > 45])
        bassi = len([n for n in pool_recenti if n <= 45])
        
        # Assegna il bonus se c'è uno squilibrio marcato (>= 36 su 60)
        bias_b = 40 if alti >= 36 else 0
        bias_a = 40 if bassi >= 36 else 0

        # 3. Assegnazione del Punteggio (Scoring)
        risultati = []
        for n in range(1, 91):
            rc = ritardi[n]
            score = 0
            
            # Punti per il Ritardo (fino a un massimo di 65 per evitare code impazzite)
            score += min(rc * 0.75, 65)
            
            # Punti Sfasamento
            score += bias_b if n <= 45 else bias_a
            
            # Punti Sincronismo (se ci sono 2 o più numeri con lo stesso ritardo)
            if list(ritardi.values()).count(rc) > 1:
                score += 15

            risultati.append({'Numero': n, 'Score': round(score, 1), 'Ritardo': rc})
        
        # Ritorna il dataframe ordinato per Score più alto
        return pd.DataFrame(risultati).sort_values('Score', ascending=False)

    # Bottone per avviare il calcolo
    if st.button("GENERA PREVISIONE RAFFINATA", type="primary"):
        res = analizza_esito(df, sigla_sel)
        top_3 = res.head(3).to_dict('records')
        
        st.subheader(f"📊 Esito Top 3 per la Ruota di {scelta_nome}")
        
        # Creazione delle "Cards" visive per i numeri
        cols = st.columns(3)
        for i, pick in enumerate(top_3):
            with cols[i]:
                st.markdown(f"""
                <div style="background-color:#1E1E1E; padding:20px; border-radius:10px; border:2px solid #00FF41; text-align:center;">
                    <h4 style="color:#FFFFFF; margin-bottom:5px;">NUMERO</h4>
                    <h1 style="color:#00FF41; font-size:65px; margin-top:0px; margin-bottom:10px;">{pick['Numero']}</h1>
                    <p style="color:#DDDDDD; font-size:18px;"><b>Score: {pick['Score']}%</b></p>
                    <p style="color:#888888; margin-bottom:0px;">Ritardo Attuale: {pick['Ritardo']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.write("---")
        
        # Spiegazione del motivo matematico
        pool_recenti = df[df['SIGLA'] == sigla_sel].iloc[::-1].head(12)[['N1', 'N2', 'N3', 'N4', 'N5']].values.flatten()
        tot_alti = len([n for n in pool_recenti if n > 45])
        tot_bassi = len([n for n in pool_recenti if n <= 45])
        
        st.info(f"**Dietro le quinte dello Sfasamento:** Nelle ultime 12 estrazioni su {scelta_nome} sono usciti **{tot_alti}** numeri Alti e **{tot_bassi}** numeri Bassi. Il sistema ha calcolato le probabilità di riequilibrio e individuato le convergenze di sincronismo.")

else:
    st.info("In attesa di leggere il file 'storico.txt'...")
