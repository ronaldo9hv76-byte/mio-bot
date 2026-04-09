import streamlit as st
import pandas as pd
import numpy as np
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Lotto Quant Analyser - Expert", layout="wide")

MAPPA_RUOTE = {
    'BA': 'Bari', 'CA': 'Cagliari', 'FI': 'Firenze', 'GE': 'Genova',
    'MI': 'Milano', 'NA': 'Napoli', 'PA': 'Palermo', 'RM': 'Roma',
    'RN': 'Nazionale', 'TO': 'Torino', 'VE': 'Venezia'
}

st.title("🎯 Lotto Quant Predictor PRO")
st.write("Analisi Sfasamento Statistico + Ricerca Posizione Determinata")

# --- CARICAMENTO DATI ---
@st.cache_data
def load_data():
    file_target = 'storico.txt'
    
    if not os.path.exists(file_target):
        st.error(f"❌ File '{file_target}' non trovato nella cartella!")
        return None

    try:
        df = pd.read_csv(file_target, sep=r'\s+', header=None, engine='python')
        df.columns = ['DATA', 'SIGLA', 'N1', 'N2', 'N3', 'N4', 'N5']
        return df
    except Exception as e:
        st.error(f"❌ Errore nella lettura del file: {e}")
        return None

df = load_data()

# --- LOGICA DEL PROGRAMMA ---
if df is not None:
    st.sidebar.success("✅ File 'storico.txt' letto con successo!")
    
    sigle_disponibili = df['SIGLA'].unique()
    opzioni_ruota = {MAPPA_RUOTE.get(s, s): s for s in sigle_disponibili}
    scelta_nome = st.sidebar.selectbox("Seleziona Ruota", list(opzioni_ruota.keys()))
    sigla_sel = opzioni_ruota[scelta_nome]

    def analizza_esito(data, sigla):
        # Filtra, inverte (più recente in cima) e resetta indice
        df_r = data[data['SIGLA'] == sigla].copy().iloc[::-1].reset_index(drop=True)
        cols_n = ['N1', 'N2', 'N3', 'N4', 'N5']
        
        # Analisi Sfasamento (Logica Roulette)
        pool_recenti = df_r.head(12)[cols_n].values.flatten()
        alti = len([n for n in pool_recenti if n > 45])
        bassi = len([n for n in pool_recenti if n <= 45])
        
        bias_b = 40 if alti >= 36 else 0
        bias_a = 40 if bassi >= 36 else 0

        risultati = []
        for n in range(1, 91):
            # 1. Calcolo Ritardo Cronologico Generale
            mask_generale = (df_r[cols_n] == n).any(axis=1)
            rc = df_r.index[mask_generale][0] if mask_generale.any() else len(df_r)

            # 2. Calcolo Ritardo per singola Posizione (1-5)
            ritardi_pos = {}
            for idx_col, col in enumerate(cols_n, start=1):
                mask_pos = (df_r[col] == n)
                ritardi_pos[idx_col] = df_r.index[mask_pos][0] if mask_pos.any() else len(df_r)
            
            # Trova la posizione in cui manca da più tempo
            miglior_posizione = max(ritardi_pos, key=ritardi_pos.get)
            ritardo_miglior_posizione = ritardi_pos[miglior_posizione]

            # 3. Scoring
            score = 0
            score += min(rc * 0.75, 65) # Punti Ritardo Base
            score += bias_b if n <= 45 else bias_a # Punti Sfasamento
            
            risultati.append({
                'Numero': n, 
                'Score': round(score, 1), 
                'Ritardo': rc,
                'Posizione': miglior_posizione,
                'Ritardo_Pos': ritardo_miglior_posizione
            })
        
        # Aggiungo Punti Sincronismo
        df_res = pd.DataFrame(risultati)
        conteggi_rc = df_res['Ritardo'].value_counts()
        for idx, row in df_res.iterrows():
            if conteggi_rc[row['Ritardo']] > 1:
                df_res.at[idx, 'Score'] += 15

        return df_res.sort_values('Score', ascending=False)

    if st.button("GENERA PREVISIONE RAFFINATA", type="primary"):
        res = analizza_esito(df, sigla_sel)
        top_3 = res.head(3).to_dict('records')
        
        st.subheader(f"📊 Esito Top 3 per la Ruota di {scelta_nome}")
        
        cols = st.columns(3)
        for i, pick in enumerate(top_3):
            with cols[i]:
                st.markdown(f"""
                <div style="background-color:#1E1E1E; padding:20px; border-radius:10px; border:2px solid #00FF41; text-align:center;">
                    <h4 style="color:#FFFFFF; margin-bottom:0px;">NUMERO</h4>
                    <h1 style="color:#00FF41; font-size:65px; margin-top:5px; margin-bottom:5px;">{pick['Numero']}</h1>
                    <div style="background-color:#333; padding:10px; border-radius:5px; margin-bottom:10px;">
                        <p style="color:#FFF; margin:0; font-size:16px;"><b>Posizione Consigliata:</b><br><span style="color:#FFD700; font-size:24px;">{pick['Posizione']}° Estratto</span></p>
                    </div>
                    <p style="color:#DDDDDD; font-size:16px; margin-bottom:2px;"><b>Score Affidabilità: {pick['Score']}%</b></p>
                    <p style="color:#888888; font-size:14px; margin-bottom:0px;">Ritardo Globale: {pick['Ritardo']} <br> Ritardo in Posizione: {pick['Ritardo_Pos']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.write("---")
        st.info("💡 **Strategia Professionale:** Gioca il numero come Estratto Semplice per coprire le spese e come Estratto Determinato nella posizione suggerita per tentare il moltiplicatore x55. Il ritardo in posizione ti indica da quante estrazioni quel numero non si presenta in quello specifico slot.")

else:
    st.info("In attesa di leggere il file 'storico.txt'...")
