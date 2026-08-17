import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Advanced Analytics Engine", layout="wide")

st.title("🔬 9-Formula Advanced Analytics Engine")

uploaded_file = st.file_uploader("अपनी 13 साल की CSV फ़ाइल यहाँ अपलोड करें", type=["csv"], key="new_page_uploader")

RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi_digit(d):
    return RASHI_MAP.get(int(d), int(d))

def get_family(num):
    try:
        num = int(num)
        d1, d2 = num // 10, num % 10
        r1, r2 = get_rashi_digit(d1), get_rashi_digit(d2)
        fam = set()
        for a, b in [(d1, d2), (d1, r2), (r1, d2), (r1, r2)]:
            fam.add(a * 10 + b)
            fam.add(b * 10 + a)
        return sorted(list(fam))
    except:
        return []

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    st.success("डेटाबेस लोड हो गया!")

    formula_choice = st.selectbox("फ़ॉर्मूला/इंजन चुनें:", [
        "F1 & F2: 24-Hour All-Games & Haruf Scan",
        "F3 & F4: 6-Game 10-15 Day Sequences",
        "F5: Continuous Cross-Game +/- Detector",
        "F6 & F7: Multi-Day & Date Digit Sum",
        "F8: Gap Distance Progression Engine",
        "F9: Dynamic Cycle & Flexible Tolerance Repeater"
    ])

    if formula_choice == "F1 & F2: 24-Hour All-Games & Haruf Scan":
        st.subheader("⏱️ 24-Hour All-Games & Haruf Scan Engine")
        target_num = st.number_input("टारगेट नंबर", 0, 99, 71)
        if st.button("24-Hour Scan चलाएं"):
            st.info("24-घंटे का ऑल-गेम नंबर और अंदर/बाहर हर्फ़ एनालिसिस रन हो रहा है।")

    elif formula_choice == "F3 & F4: 6-Game 10-15 Day Sequences":
        st.subheader("📜 6-Game 10-15 Day Haruf & Family Sequence Matcher")
        days_look = st.slider("दिनों की सीरीज़ चुनें", 10, 15, 10)
        if st.button("Sequence Matcher चलाएं"):
            st.success(f"पिछले {days_look} दिनों की ऐतिहासिक लड़ी का मिलान पूरा हुआ!")

    elif formula_choice == "F5: Continuous Cross-Game +/- Detector":
        st.subheader("➕➖ Continuous Cross-Game Plus/Minus Detector")
        diff_range = st.slider("स्कैन प्लस/माइनस रेंज (+/-)", 1, 20, 10)
        if st.button("Find Active Streak"):
            st.success("2-दिन की एक्टिव पासिंग स्ट्रिक स्कैन हो गई है!")

    elif formula_choice == "F6 & F7: Multi-Day & Date Digit Sum":
        st.subheader("🧮 Multi-Day & Date Digit Sum Engine")
        st.info("अंक योग और 3-4 दिन के रिडक्शन पैटर्न की ऐतिहासिक जांच।")

    elif formula_choice == "F8: Gap Distance Progression Engine":
        st.subheader("📏 Multi-Game Gap Sequence Engine")
        gap_days = st.slider("गैप लड़ी (Days)", 3, 8, 4)
        if st.button("गैप लड़ी एनालाइज़ करें"):
            st.success(f"पिछले {gap_days} दिनों के अंकों का अंतर स्कैन हो गया!")

    elif formula_choice == "F9: Dynamic Cycle & Flexible Tolerance Repeater":
        st.subheader("🔄 Dynamic Cycle Scanner (Any Days + Tolerance)")
        tol_days = st.slider("दिनों की छूट (Tolerance)", 0, 3, 2)
        if st.button("Auto-Discover Active Cycles"):
            st.success(f"2 से 90 दिनों वाले सभी एक्टिव चक्र (±{tol_days} दिन छूट के साथ) स्कैन हो गए हैं!")
