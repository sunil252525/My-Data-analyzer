import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="All-in-One Analytics Dashboard", layout="wide")

st.title("📊 All-in-One 9-Formula Dashboard")

uploaded_file = st.file_uploader("अपनी 13 साल की CSV फ़ाइल यहाँ अपलोड करें", type=["csv"], key="dashboard_uploader")

# ================= HELPER FUNCTIONS =================
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

def get_haruf(num):
    try:
        num = int(num)
        return num // 10, num % 10
    except:
        return None, None

def get_digit_sum(num):
    try:
        num = int(num)
        return (num // 10 + num % 10)
    except:
        return 0

def get_digital_root(num):
    try:
        s = get_digit_sum(num)
        return s if s < 10 else (s // 10 + s % 10)
    except:
        return 0

def get_digit_gap(num):
    try:
        num = int(num)
        return abs((num // 10) - (num % 10))
    except:
        return 0

# ================= MAIN DASHBOARD =================
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    st.success("✅ 13 साल का डेटाबेस सफलतापूर्वक लोड हो गया! नीचे सभी 9 फ़ॉर्मूलों के नतीजे एक साथ देख सकते हैं।")

    # ---------------- GLOBAL INPUTS ----------------
    st.markdown("---")
    st.header("🎯 मास्टर इनपुट (ग्लोबल सेटिंग्स)")
    c1, c2 = st.columns(2)
    with c1:
        g_sel = st.selectbox("गेम चुनें (F1/F2 फ़ॉर्मूला हेतु):", available_cols)
    with c2:
        target_num = st.number_input("टारगेट नंबर दर्ज करें:", 0, 99, 58)

    st.markdown("---")

    # ================= FORMULAS 1 & 2 =================
    st.subheader("1️⃣ & 2️⃣ 24-Hour All-Games Number, Family & Haruf Engine")
    matches = df[df[g_sel] == target_num].index
    total_matches = len(matches)
    
    if total_matches > 0:
        next_numbers, haruf_in, haruf_out = [], [], []
        family_hits = 0
        target_fam = get_family(target_num)

        for idx in matches:
            if idx + 1 < len(df):
                for c in available_cols:
                    val = df.loc[idx + 1, c]
                    if pd.notna(val):
                        val_int = int(val)
                        next_numbers.append(val_int)
                        h_i, h_o = get_haruf(val_int)
                        if h_i is not None: haruf_in.append(h_i)
                        if h_o is not None: haruf_out.append(h_o)
                        if val_int in target_fam:
                            family_hits += 1

        total_ops = len(next_numbers)
        top_nums = pd.Series(next_numbers).value_counts().head(5).to_dict() if next_numbers else {}
        top_in = pd.Series(haruf_in).value_counts().head(3).to_dict() if haruf_in else {}
        top_out = pd.Series(haruf_out).value_counts().head(3).to_dict() if haruf_out else {}
        fam_rate = round((family_hits / total_ops)*100, 2) if total_ops > 0 else 0

        res_df = pd.DataFrame([{
            "कुल ऐतिहासिक मैच": total_matches,
            "24 घंटे मौक़े": total_ops,
            "टॉप 5 रिपीट नंबर": str(top_nums),
            "फैमिली पासिंग दर (%)": f"{fam_rate}%",
            "टॉप अंदर हर्फ़": str(top_in),
            "टॉप बाहर हर्फ़": str(top_out)
        }])
        st.table(res_df)
    else:
        st.warning("इस गेम में यह नंबर दर्ज नहीं मिला।")

    st.markdown("---")

    # ================= FORMULAS 3 & 4 =================
    st.subheader("3️⃣ & 4️⃣ 6-Game 10-15 Day Sequence Matcher")
    recent_df = df.tail(10)[available_cols]
    st.write("📌 **हाल ही के 10 दिनों की सीरीज़ Matrix:**")
    st.dataframe(recent_df.tail(3))

    last_harufs = []
    for idx, row in recent_df.iterrows():
        for c in available_cols:
            if pd.notna(row[c]):
                last_harufs.append(get_haruf(row[c]))

    target_sub = last_harufs[-3:]
    matched_next_harufs = []
    
    for i in range(len(df) - 11):
        hist_slice = [get_haruf(df.loc[i, c]) for c in available_cols if pd.notna(df.loc[i, c])]
        if hist_slice[-3:] == target_sub and i + 1 < len(df):
            next_val = df.loc[i+1, available_cols[0]]
            if pd.notna(next_val):
                matched_next_harufs.append(get_haruf(next_val)[0])

    top_next = pd.Series(matched_next_harufs).value_counts().head(3).to_dict() if matched_next_harufs else "कोई पर्याप्त ऐतिहासिक मैच नहीं मिला"
    st.info(f"🎯 **हर्फ़ लड़ी रिजल्ट:** इस लड़ी के बाद आने वाले सबसे मजबूत हर्फ़: `{top_next}`")

    st.markdown("---")

    # ================= FORMULA 5 =================
    st.subheader("5️⃣ Continuous Cross-Game Plus/Minus Detector (+/-)")
    flat_results = []
    for idx in range(len(df)-3, len(df)):
        for c in available_cols:
            if pd.notna(df.loc[idx, c]):
                flat_results.append(int(df.loc[idx, c]))
    
    diff_tracker = []
    for i in range(len(flat_results)-1):
        diff = (flat_results[i+1] - flat_results[i]) % 100
        if diff <= 10 or (100 - diff) <= 10:
            diff_tracker.append(diff)

    top_diffs = pd.Series(diff_tracker).value_counts().head(5).to_dict() if diff_tracker else {}
    st.write(pd.DataFrame([{"पिछले 48 घंटों में एक्टिव +/- अंतराल और फ्रीक्वेंसी": str(top_diffs)}]))

    st.markdown("---")

    # ================= FORMULAS 6 & 7 =================
    st.subheader("6️⃣ & 7️⃣ Multi-Day & Date Digit Sum Engine")
    recent_sums = []
    for idx in range(len(df)-4, len(df)):
        for c in available_cols:
            if pd.notna(df.loc[idx, c]):
                recent_sums.append(get_digit_sum(df.loc[idx, c]))
    
    curr_seq = recent_sums[-3:]
    st.write(f"📌 **पिछले 3 खेलों का डिजिट सम क्रम:** `{curr_seq}`")
    
    recent_roots = [get_digital_root(df.loc[len(df)-1, c]) for c in available_cols if pd.notna(df.loc[len(df)-1, c])]
    st.info(f"🎯 **तारीख रिडक्शन डिजिटल रूट:** `{recent_roots}`")

    st.markdown("---")

    # ================= FORMULA 8 =================
    st.subheader("8️⃣ Gap Distance Progression Engine")
    recent_gaps = []
    for idx in range(len(df)-4, len(df)):
        for c in available_cols:
            if pd.notna(df.loc[idx, c]):
                recent_gaps.append(get_digit_gap(df.loc[idx, c]))
    
    curr_gap_seq = recent_gaps[-4:]
    st.write(f"📌 **वर्तमान डिजिट गैप सीरीज़ (अंतर):** `{curr_gap_seq}`")

    st.markdown("---")

    # ================= FORMULA 9 =================
    st.subheader("9️⃣ Dynamic Cycle & Flexible Tolerance Repeater")
    due_items = []
    last_idx = len(df) - 1

    for num in range(100):
        indices = df[df[available_cols[0]] == num].index.tolist()
        if len(indices) >= 2:
            gaps = [indices[i] - indices[i-1] for i in range(1, len(indices))]
            avg_gap = int(np.mean(gaps))
            days_since_last = last_idx - indices[-1]
            
            if abs(days_since_last - avg_gap) <= 2:
                due_items.append({"नंबर": num, "औसत साइकिल गैप (दिन)": avg_gap, "पेंडिंग दिन": days_since_last})

    if due_items:
        st.write("🔥 **आज साइकिल चक्र पूरा करने वाले संभावित नंबर:**")
        st.dataframe(pd.DataFrame(due_items).head(10))
    else:
        st.info("आज के लिए कोई पेंडिंग साइकिल अलर्ट नहीं है।")
