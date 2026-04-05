import streamlit as st
import numpy as np
import pandas as pd
from scipy.stats import poisson

# — CONFIGURAZIONE —

st.set_page_config(page_title=“GOTHIC ORACLE v10.0 SYNDICATE”, layout=“wide”)

st.markdown(”””
<style>
@import url(‘https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&display=swap’);

```
.stApp { background-color: #050505; color: #e0e0e0; }

h1, .gothic-title {
    font-family: 'UnifrakturMaguntia', cursive;
    color: #ff0000;
    text-align: center;
    font-size: 3.5rem !important;
    text-shadow: 0 0 20px #ff0000aa;
}

.version-tag {
    text-align: center;
    color: #888;
    font-size: 0.85rem;
    margin-top: -10px;
    margin-bottom: 20px;
    letter-spacing: 3px;
}

.stButton>button {
    width: 100%;
    background-color: #1a0000;
    color: #ff4444;
    font-weight: 900;
    border: 2px solid #ff0000;
    font-size: 1.1rem;
    padding: 12px;
    transition: all 0.3s;
}
.stButton>button:hover {
    background-color: #ff0000;
    color: white;
}

.warning-box {
    background-color: #2a1a00;
    border-left: 4px solid #ff8800;
    padding: 10px 15px;
    border-radius: 4px;
    margin: 5px 0;
    font-size: 0.9rem;
}

.metric-card {
    background-color: #111;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 15px;
    text-align: center;
    margin: 5px 0;
}

.metric-card .label {
    font-size: 0.75rem;
    color: #888;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.metric-card .value {
    font-size: 1.8rem;
    font-weight: 900;
    color: #ff4444;
}

.kelly-box {
    background-color: #001a00;
    border: 1px solid #00aa00;
    border-radius: 6px;
    padding: 10px 15px;
    text-align: center;
    font-size: 1.1rem;
    font-weight: bold;
    color: #00ff44;
}
</style>
""", unsafe_allow_html=True)
```

# ─────────────────────────────────────────────

# UTILS

# ─────────────────────────────────────────────

def validate_row(row):
“”“Controlla anomalie nei dati di input e restituisce lista di warning.”””
warnings = []
xg_cols = [‘xG_Home’, ‘xGA_Home’, ‘xG_Away’, ‘xGA_Away’]
for col in xg_cols:
v = row.get(col, None)
if pd.notna(v):
try:
v = float(str(v).replace(’,’, ‘.’))
if v > 4.0:
warnings.append(f”⚠️ {col} = {v} sembra anomalo (>4.0)”)
if v <= 0:
warnings.append(f”⚠️ {col} = {v} non valido (<=0)”)
except:
warnings.append(f”⚠️ {col} non è un numero valido”)
for col in [‘ELO_Home’, ‘ELO_Away’]:
v = row.get(col, None)
if pd.notna(v):
try:
v = float(str(v).replace(’,’, ‘.’))
if v < 1000 or v > 2500:
warnings.append(f”⚠️ {col} = {v} fuori range atteso (1000-2500)”)
except:
warnings.append(f”⚠️ {col} non è un numero valido”)
for col in [‘Quota1’, ‘QuotaX’, ‘Quota2’]:
v = row.get(col, None)
if pd.notna(v):
try:
v = float(str(v).replace(’,’, ‘.’))
if v < 1.01 or v > 30:
warnings.append(f”⚠️ {col} = {v} fuori range (1.01-30)”)
except:
warnings.append(f”⚠️ {col} non è un numero valido”)
return warnings

def clean(val, default=1.2):
“”“Pulisce e converte un valore numerico.”””
if pd.isna(val):
return default
if isinstance(val, str):
val = val.replace(’,’, ‘.’)
try:
v = float(val)
return v if v > 0 else default
except:
return default

# ─────────────────────────────────────────────

# DIXON-COLES CORRECTION

# ─────────────────────────────────────────────

def dixon_coles_correction(home_goals, away_goals, lh, la, rho=-0.13):
“””
Fattore correttivo Dixon-Coles per score bassi (0-0, 1-0, 0-1, 1-1).
rho negativo riduce la probabilità di 1-0 / 0-1 e aumenta quella di 0-0.
“””
if home_goals == 0 and away_goals == 0:
return 1 - lh * la * rho
elif home_goals == 0 and away_goals == 1:
return 1 + lh * rho
elif home_goals == 1 and away_goals == 0:
return 1 + la * rho
elif home_goals == 1 and away_goals == 1:
return 1 - rho
else:
return 1.0

def compute_prob_dc(lh, la, max_goals=6, rho=-0.13):
“””
Calcola P(home_goals, away_goals) con correzione Dixon-Coles.
Restituisce p1, pX, p2, p_goal, p_over25.
“””
p1, px, p2 = 0.0, 0.0, 0.0
p_goal = 0.0
p_over25 = 0.0
total_prob = 0.0

```
for h in range(max_goals + 1):
    for a in range(max_goals + 1):
        p_base = poisson.pmf(h, lh) * poisson.pmf(a, la)
        p_dc = p_base * dixon_coles_correction(h, a, lh, la, rho)
        total_prob += p_dc

        if h > a:
            p1 += p_dc
        elif h == a:
            px += p_dc
        else:
            p2 += p_dc

        if h > 0 and a > 0:
            p_goal += p_dc
        if h + a > 2.5:
            p_over25 += p_dc

# Normalizza per sicurezza
if total_prob > 0:
    p1 /= total_prob
    px /= total_prob
    p2 /= total_prob
    p_goal /= total_prob
    p_over25 /= total_prob

return p1, px, p2, p_goal, p_over25
```

# ─────────────────────────────────────────────

# ENGINE PRINCIPALE

# ─────────────────────────────────────────────

def analyze_full_syndicate(row):
try:
xh  = clean(row[‘xG_Home’])
xah = clean(row[‘xGA_Home’])
eh  = clean(row[‘ELO_Home’], default=1500)
xa  = clean(row[‘xG_Away’])
xaa = clean(row[‘xGA_Away’])
ea  = clean(row[‘ELO_Away’], default=1500)
q1  = clean(row[‘Quota1’])
qX  = clean(row[‘QuotaX’])
q2  = clean(row[‘Quota2’])

```
    # ── 1. POISSON ENGINE con correzione ELO ──────────────────────────────
    elo_diff = (eh - ea) / 400
    l_h = ((xh + xaa) / 2) * (1.2 ** elo_diff)
    l_a = ((xa + xah) / 2) * (1.2 ** -elo_diff)

    # Clamp lambda per evitare esplosioni
    l_h = np.clip(l_h, 0.1, 6.0)
    l_a = np.clip(l_a, 0.1, 6.0)

    # ── 2. PROBABILITÀ CON DIXON-COLES ────────────────────────────────────
    p1, px, p2, p_goal, p_uo25 = compute_prob_dc(l_h, l_a)

    # ── 3. MARKOV STABILITY INDEX (ricalibrato) ────────────────────────────
    # Dominance: range reale [0, 1] — differenza ELO normalizzata su 600 pt
    prob_dominance = min(abs(eh - ea) / 600, 1.0)

    # Scoring efficiency: quanto xG è effettivo vs difesa
    total_xg = xh + xa + xah + xaa + 0.1
    prob_scoring_efficiency = (xh + xa) / total_xg

    markov_index = (prob_dominance * 0.6) + (prob_scoring_efficiency * 0.4)

    # ── 4. EDGE & BEST SIGN ───────────────────────────────────────────────
    candidates = [
        (p1, q1, "1"),
        (px, qX, "X"),
        (p2, q2, "2"),
    ]
    best_p, best_q, label = max(candidates, key=lambda x: x[0] * x[1])
    edge = (best_p * best_q) - 1

    # ── 5. KELLY CRITERION ────────────────────────────────────────────────
    # Kelly % = (p * (q-1) - (1-p)) / (q-1)
    # Usiamo half-Kelly per prudenza
    if best_q > 1 and edge > 0:
        kelly_full = (best_p * (best_q - 1) - (1 - best_p)) / (best_q - 1)
        kelly = max(0.0, kelly_full * 0.5)  # half-Kelly
    else:
        kelly = 0.0

    return p1, px, p2, p_goal, p_uo25, markov_index, edge, label, best_p, kelly

except Exception as e:
    return [0.33, 0.33, 0.33, 0.5, 0.5, 0.3, 0.0, "N/A", 0.33, 0.0]
```

# ─────────────────────────────────────────────

# CONSIGLIO (SOGLIE RICALIBRATE)

# ─────────────────────────────────────────────

def give_advice(edge, stability_val):
“””
Soglie ricalibrate sul nuovo Markov Index (range reale 0.15 - 0.65).
CASSA FORTE: edge > 5% E stabilità ALTA (>=0.40 nel nuovo sistema)
SINGOLA FOLLE: edge molto alto ma stabilità bassa (partita imprevedibile)
VALUTARE: c’è valore ma non abbastanza certezza
EVITA: edge negativo, il mercato batte il modello
“””
if edge > 0.05 and stability_val >= 0.40:
return “CASSA FORTE 💰”
if edge > 0.12 and stability_val < 0.40:
return “SINGOLA FOLLE 🧨”
if 0 < edge <= 0.05:
return “VALUTARE 🔍”
if edge < 0:
return “EVITA ❌”
return “VALUTARE 🔍”

# ─────────────────────────────────────────────

# UI

# ─────────────────────────────────────────────

st.markdown(’<div class="gothic-title">Gothic Oracle v10.0: The Syndicate</div>’, unsafe_allow_html=True)
st.markdown(’<div class="version-tag">▸ DIXON-COLES · KELLY CRITERION · MARKOV RICALIBRATO ◂</div>’, unsafe_allow_html=True)

with st.expander(“📖 Guida al sistema”):
st.markdown(”””
**Novità v10.0:**
- **Dixon-Coles**: corregge la sovrastima Poisson dei risultati 0-0, 1-0, 0-1 e 1-1
- **Kelly Criterion (Half)**: suggerisce la % di bankroll da puntare. Es: Kelly 3.2% = scommetti il 3.2% del tuo bankroll
- **Markov ricalibrato**: range reale 0-1, soglia CASSA FORTE abbassata a 0.40
- **Warning automatici**: avvisa se i dati di input sembrano anomali
- **CONSIGLIO aggiornato**: CASSA FORTE ora raggiungibile con dati realistici

```
**Colonne output:**
| Colonna | Significato |
|---|---|
| BEST_SIGN | Segno con maggior valore atteso |
| BOT_PROB | Probabilità modello per BEST_SIGN |
| EDGE | Vantaggio sul bookmaker (>5% = valore) |
| KELLY% | % bankroll consigliata (Half-Kelly) |
| CONSIGLIO | Raccomandazione finale |
| STABILITÀ | Affidabilità previsione |
""")
```

uploaded_file = st.file_uploader(“Carica Excel (Richiede xG, xGA, ELO e QUOTE)”, type=“xlsx”)

if uploaded_file:
df = pd.read_excel(uploaded_file)

```
# Pulizia colonne numeriche
num_cols = ['xG_Home', 'xGA_Home', 'ELO_Home', 'xG_Away', 'xGA_Away', 'ELO_Away', 'Quota1', 'QuotaX', 'Quota2']
for col in num_cols:
    if col in df.columns and df[col].dtype == object:
        df[col] = df[col].astype(str).str.replace(',', '.').astype(float)

# Verifica colonne obbligatorie
missing_cols = [c for c in num_cols if c not in df.columns]
if missing_cols:
    st.error(f"❌ Colonne mancanti nel file: {', '.join(missing_cols)}")
    st.stop()

# Warning per dati anomali
all_warnings = []
for i, row in df.iterrows():
    w = validate_row(row)
    if w:
        home = row.get('Home', f'Riga {i}')
        away = row.get('Away', '')
        for msg in w:
            all_warnings.append(f"**{home} vs {away}** — {msg}")

if all_warnings:
    with st.expander(f"⚠️ {len(all_warnings)} avviso/i sui dati di input (clicca per vedere)"):
        for w in all_warnings:
            st.markdown(f'<div class="warning-box">{w}</div>', unsafe_allow_html=True)

st.markdown(f"**{len(df)} partita/e caricate.** Pronto per l'analisi.")

if st.button("🔥 ESEGUI ANALISI TOTALE"):
    with st.spinner("Calcolo in corso con Dixon-Coles..."):
        res = df.apply(analyze_full_syndicate, axis=1)
        res_df = pd.DataFrame(
            res.tolist(),
            columns=['P1', 'PX', 'P2', 'P_GOAL', 'P_UO25', 'MARKOV_VAL', 'EDGE', 'BEST_SIGN', 'BOT_PROB', 'KELLY'],
            index=df.index
        )

        df = df.reset_index(drop=True)
        res_df = res_df.reset_index(drop=True)
        df = pd.concat([df, res_df], axis=1)

        # Etichette derivate
        df['GOAL/NOGOAL'] = df['P_GOAL'].apply(lambda x: 'GOAL' if x > 0.52 else 'NO GOAL')
        df['U/O 2,5']     = df['P_UO25'].apply(lambda x: 'OVER 2.5' if x > 0.55 else 'UNDER 2.5')

        df['STABILITÀ'] = df['MARKOV_VAL'].apply(
            lambda x: 'ALTA 🔒' if x >= 0.40 else ('MEDIA ⚠️' if x >= 0.25 else 'BASSA 🧨')
        )
        df['CONSIGLIO'] = df.apply(lambda r: give_advice(r['EDGE'], r['MARKOV_VAL']), axis=1)

    # ── METRICHE RIEPILOGATIVE ───────────────────────────────────────────
    n_cassa   = (df['CONSIGLIO'] == 'CASSA FORTE 💰').sum()
    n_singola = (df['CONSIGLIO'] == 'SINGOLA FOLLE 🧨').sum()
    n_evita   = (df['CONSIGLIO'] == 'EVITA ❌').sum()
    n_valuta  = (df['CONSIGLIO'] == 'VALUTARE 🔍').sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="label">CASSA FORTE</div><div class="value" style="color:#00ff44">{n_cassa}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="label">SINGOLA FOLLE</div><div class="value" style="color:#ff8800">{n_singola}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="label">VALUTARE</div><div class="value" style="color:#aaaaaa">{n_valuta}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="label">EVITA</div><div class="value" style="color:#ff4444">{n_evita}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TABELLA PRINCIPALE ───────────────────────────────────────────────
    view = ['Home', 'Away', 'BEST_SIGN', 'BOT_PROB', 'EDGE', 'KELLY', 'CONSIGLIO', 'GOAL/NOGOAL', 'U/O 2,5', 'STABILITÀ', 'MARKOV_VAL']

    def color_cell(val, col_name):
        pos_keywords = ['GOAL', 'OVER', 'ALTA', 'CASSA', '1', '2']
        neg_keywords = ['BASSA', '🧨', 'EVITA', '❌', 'NO GOAL', 'UNDER']
        neutral_keywords = ['MEDIA', 'VALUTARE', 'X', '🔍']

        if col_name == 'EDGE':
            if isinstance(val, (int, float)):
                return 'background-color: #006400; color: white' if val > 0.05 else 'background-color: #8B0000; color: white'
        if col_name == 'KELLY':
            if isinstance(val, (int, float)):
                if val > 0.05:
                    return 'background-color: #004400; color: #00ff44; font-weight:bold'
                elif val > 0:
                    return 'background-color: #002200; color: #88ff88'
                else:
                    return 'background-color: #1a0000; color: #666'

        s = str(val)
        if any(k in s for k in neg_keywords):
            return 'background-color: #8B0000; color: white; font-weight: bold'
        if any(k in s for k in neutral_keywords):
            return 'background-color: #4a3800; color: #ffcc44; font-weight: bold'
        if any(k in s for k in pos_keywords):
            return 'background-color: #006400; color: white; font-weight: bold'
        return ''

    styled_df = (
        df[view].style
        .format({
            'MARKOV_VAL': '{:.1%}',
            'EDGE':       '{:.1%}',
            'BOT_PROB':   '{:.1%}',
            'KELLY':      '{:.1%}',
        })
        .map(lambda x: color_cell(x, 'EDGE'),   subset=['EDGE'])
        .map(lambda x: color_cell(x, 'KELLY'),  subset=['KELLY'])
        .map(lambda x: color_cell(x, 'OTHER'),  subset=['GOAL/NOGOAL', 'U/O 2,5', 'STABILITÀ', 'BEST_SIGN', 'CONSIGLIO'])
    )

    st.dataframe(styled_df, use_container_width=True)

    # ── DETTAGLIO PROBABILITÀ PER PARTITA ───────────────────────────────
    st.markdown("### 📊 Dettaglio Probabilità per Partita")
    for _, row in df.iterrows():
        home = row.get('Home', '?')
        away = row.get('Away', '?')
        with st.expander(f"🔍 {home} vs {away}  —  {row['CONSIGLIO']}"):
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("P(1)",  f"{row['P1']:.1%}")
            c2.metric("P(X)",  f"{row['PX']:.1%}")
            c3.metric("P(2)",  f"{row['P2']:.1%}")
            c4.metric("GOAL",  f"{row['P_GOAL']:.1%}")
            c5.metric("O2.5",  f"{row['P_UO25']:.1%}")

            if row['KELLY'] > 0:
                st.markdown(
                    f'<div class="kelly-box">💼 Kelly consigliato: punta il <b>{row["KELLY"]:.1%}</b> del tuo bankroll su <b>{row["BEST_SIGN"]}</b> @ {clean(row.get("Quota" + ("1" if row["BEST_SIGN"]=="1" else ("X" if row["BEST_SIGN"]=="X" else "2")), 1.0)):.2f}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.info("Nessun valore positivo — Kelly = 0%, non puntare.")

    st.success("✅ Analisi v10.0 completata: Dixon-Coles attivo · Kelly Criterion calcolato · Markov ricalibrato.")
```
