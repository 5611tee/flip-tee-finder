
import streamlit as st
import pandas as pd
import re
from math import floor

st.set_page_config(page_title="Flip Tee Finder", page_icon="👕")
st.title("👕 Flip Tee Finder")
st.caption("Score vintage T‑shirts for quick‑flip potential and get a listing checklist.")

@st.cache_data
def load_data():
    tags = pd.read_csv("data/valuable_tags.csv")
    kw = pd.read_csv("data/high_value_keywords.csv")
    return tags, kw

tags, kw = load_data()

# --- Sidebar: What to look for cheat sheet ---
with st.sidebar:
    st.header("What to look for")
    st.markdown(
        "- **Single‑stitch** hems/sleeves (80s–early 90s)\n"
        "- **Made in USA/Mexico/Canada** (older)\n"
        "- **Tour dates** on back = stronger value\n"
        "- **All‑over / Liquid Blue / tie‑dye** prints\n"
        "- **Band/artist licensing** (199x)\n"
        "- Desirable tags: Brockum, Giant, Liquid Blue, 3D Emblem, Screen Stars\n"
        "- **Large sizes (L–XXL)** flip faster\n"
        "- Good **front+back hits**\n"
        "- **Y2K** pop culture & gaming"
    )
    st.divider()
    st.write("⚠️ Red flags")
    st.markdown(
        "- Crisp double‑stitch w/ modern RN = likely reprint\n"
        "- Super heavy modern blanks (e.g., 2000s+ Gildan)\n"
        "- Blurry DTG prints on old blanks"
    )

st.subheader("Describe the tee")
col1, col2 = st.columns(2)
with col1:
    title = st.text_input("Title / main graphic words (e.g., 'Nirvana In Utero 1993 tour')", "")
    era = st.selectbox("Era (best guess)", ["Unknown","1970s","1980s","1990s","Y2K (2000–2004)","Modern (2005+)"])
    category = st.selectbox("Category", ["Band","Hip-Hop","Movie/TV","Sports/Collegiate","Moto/Trucking","Tech/Gaming","Art/Design","Other"])
    size = st.selectbox("Size", ["XS","S","M","L","XL","XXL","Unknown"])
with col2:
    tag = st.selectbox("Tag/Blank", ["Unknown"] + sorted(tags["tag"].unique().tolist()))
    single_stitch = st.checkbox("Single‑stitch hem/sleeve")
    made = st.selectbox("Made in …", ["Unknown","USA","Mexico","Canada","Europe","Other Asia"])
    front_back = st.selectbox("Print placement", ["Front only","Back only","Front + Back","All‑over"])
    condition = st.selectbox("Condition", ["Deadstock / NWT","Excellent","Good (light wear)","Distressed (holes/fades)","Heavily thrashed"])

st.subheader("Score")

def base_score(era, category):
    s = 10
    if era=="1980s": s+=30
    if era=="1990s": s+=35
    if era=="Y2K (2000–2004)": s+=22
    if era=="1970s": s+=28
    if category in ["Band","Hip-Hop","Tech/Gaming","Moto/Trucking"]: s+=12
    return s

def feature_score(tag, single_stitch, made, front_back, size, condition):
    s = 0
    # tag weight
    try:
        s += int(pd.read_csv("data/valuable_tags.csv").set_index("tag").loc[tag,"weight"]) if tag!="Unknown" else 0
    except:
        s += 0
    if single_stitch: s += 12
    if made in ["USA","Mexico","Canada","Europe"]: s += 6
    if front_back=="Front + Back": s += 6
    if front_back=="All‑over": s += 10
    if size in ["L","XL","XXL"]: s += 6
    if condition=="Deadstock / NWT": s += 10
    if condition=="Excellent": s += 8
    if condition=="Good (light wear)": s += 5
    if condition=="Distressed (holes/fades)": s += 4  # still sells
    if condition=="Heavily thrashed": s -= 4
    return s

def keyword_boost(text):
    s = 0
    text_low = text.lower()
    data = kw.copy()
    for _, row in data.iterrows():
        if re.search(r"\b"+re.escape(row["keyword"].lower())+r"\b", text_low):
            s += int(row["weight"])
    return s

score = base_score(era, category) + feature_score(tag, single_stitch, made, front_back, size, condition) + keyword_boost(title)
score = max(0, min(100, score))

st.metric("Quick‑Flip Score (0–100)", value=score)

# Pricing guidance (very rough heuristics)
def price_band(score, era):
    base_low, base_high = 15, 45
    if era in ["1980s","1990s"]: base_low, base_high = 40, 160
    if era=="Y2K (2000–2004)": base_low, base_high = 35, 120
    if era=="1970s": base_low, base_high = 60, 200
    low = floor(base_low + (score/100)*0.8*base_low)
    high = floor(base_high + (score/100)*0.8*base_high)
    return low, high

low, high = price_band(score, era)
st.write(f"**Suggested list price range:** ${low}–${high} (aim higher on auctions if demand keywords match).")

# Notes & checklist
st.subheader("Listing helper")
bullets = []
if single_stitch: bullets.append("Single‑stitch hems/sleeves")
if tag!="Unknown": bullets.append(f"Original tag: {tag}")
if made!="Unknown": bullets.append(f"Made in {made}")
if "tour" in title.lower(): bullets.append("Tour dates on back? photograph clearly")
if "promo" in title.lower(): bullets.append("Promo issue – note licensing and year")
if front_back in ["Front + Back","All‑over"]: bullets.append(f"Print placement: {front_back}")
if size in ["L","XL","XXL"]: bullets.append("Sought‑after larger size")
if condition in ["Distressed (holes/fades)","Heavily thrashed"]:
    bullets.append("Describe flaws honestly; measure pit‑to‑pit & length")

st.write("- " + "\n- ".join(bullets) if bullets else "_Add details above to generate tips._")

# SEO title generator
def gen_title(title, era, tag, size):
    parts = []
    if era!="Unknown": parts.append(era)
    if title: parts.append(title)
    if tag not in ["Unknown","Single Stitch (feature)"]: parts.append(tag)
    if size!="Unknown": parts.append(size)
    parts.append("Vintage T‑Shirt")
    return " | ".join(parts)

st.text_input("Suggested listing title", gen_title(title, era, tag, size))

# Red flags
st.subheader("Potential red flags")
warns = []
if not single_stitch and era in ["1980s","1990s"]:
    warns.append("Double‑stitch on an 80s/early‑90s design: double‑check authenticity/licensing.")
if tag in ["Delta Pro Weight"] and era in ["1980s"]:
    warns.append("Delta Pro Weight is typically 90s+; verify date.")
if "Gildan" in tag:
    warns.append("Modern blank; check if it’s a reprint.")
st.write("- " + "\n- ".join(warns) if warns else "_No obvious red flags from inputs._")

st.divider()
st.caption("Heuristic tool for sourcing and fast flips. Use comps on eBay/Depop for final pricing.")
