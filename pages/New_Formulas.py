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
        if pd.isna(num): return []
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
        if pd.isna(num): return None, None
        num = int(num)
        return num // 10, num % 10
    except:
        return None, None

def get_haruf_rashi(num):
    try:
        h_i, h_o = get_haruf(num)
        if h_i is None: return None, None
        return get_rashi_digit(h_i), get_rashi_digit(h_o)
    except:
        return None, None

def get_digit_sum(num):
    try:
        if pd.isna(num): return 0
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
        if pd.isna(num): return 0
        num = int(num)
        return abs((num // 10) - (num % 10))
    except:
        return 0

# ================= MAIN DASHBOARD =================
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Preserve original Date column if present
    date_col = 'Date' if 'Date' in df.columns else None
    
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    
    df = df.dropna(subset=available_cols, how='all').reset_index(drop=True)

    st.success("✅ 13 साल का डेटाबेस सफलतापूर्वक लोड हो गया!")

    # ---------------- GLOBAL INPUTS ----------------
    st.markdown("---")
    st.header("🎯 मास्टर इनपुट (ग्लोबल सेटिंग्स)")
    c1, c2 = st.columns(2)
    with c1:
        g_sel = st.selectbox("मुख्य गेम चुनें (करंट पैटर्न हेतु):", available_cols)
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

    # ================= FORMULAS 3 & 4 (ADVANCED FLEXIBLE SEQUENCE MATCHER) =================
    st.subheader("3️⃣ & 4️⃣ 6-Game Flexible Pattern & Rashi/Haruf Sequence Engine")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        seq_days = st.slider("लड़ी कितने दिनों की लें (Pattern Days):", 3, 10, 5, key="seq_slider")
    with col_s2:
        match_mode = st.selectbox(
            "मैचिंग का प्रकार चुनें (Search Mode):",
            [
                "1. Family Sequence (फैमिली लड़ी मैच)",
                "2. Inside Haruf / Rashi (अंदर हर्फ़ व राशि लड़ी)",
                "3. Outside Haruf / Rashi (बाहर हर्फ़ व राशि लड़ी)",
                "4. Exact Numbers (हूबहू नंबर)"
            ]
        )

    clean_series = df[g_sel].dropna().astype(int).tolist()
    recent_nums = clean_series[-seq_days:] if len(clean_series) >= seq_days else clean_series
    
    st.write(f"📌 **`{g_sel}` का हालिया {len(recent_nums)} दिनों का नंबर पैटर्न:** `{recent_nums}`")

    # Historical Pattern Search Logic
    match_records = []
    
    for c in available_cols:
        col_vals = df[c].tolist()
        for i in range(len(col_vals) - len(recent_nums) - 1):
            sub_seq = col_vals[i : i + len(recent_nums)]
            if any(pd.isna(v) for v in sub_seq):
                continue
            
            sub_seq = [int(v) for v in sub_seq]
            is_match = False
            
            if "1. Family Sequence" in match_mode:
                # Check if each number in history falls into the family of current sequence
                is_match = all(sub_seq[k] in get_family(recent_nums[k]) for k in range(len(recent_nums)))
            
            elif "2. Inside Haruf" in match_mode:
                # Check inside haruf or its rashi
                is_match = all(
                    get_haruf(sub_seq[k])[0] in (get_haruf(recent_nums[k])[0], get_haruf_rashi(recent_nums[k])[0])
                    for k in range(len(recent_nums))
                )

            elif "3. Outside Haruf" in match_mode:
                # Check outside haruf or its rashi
                is_match = all(
                    get_haruf(sub_seq[k])[1] in (get_haruf(recent_nums[k])[1], get_haruf_rashi(recent_nums[k])[1])
                    for k in range(len(recent_nums))
                )

            elif "4. Exact Numbers" in match_mode:
                is_match = (sub_seq == recent_nums)

            if is_match:
                next_val = col_vals[i + len(recent_nums)]
                if pd.notna(next_val):
                    rec_date = df.loc[i + len(recent_nums), date_col] if date_col else f"Row #{i + len(recent_nums)}"
                    match_records.append({
                        "मैच हुई तारीख/इंडेक्स": rec_date,
                        "गेम नाम": c,
                        "ऐतिहासिक लड़ी": str(sub_seq),
                        "अगले दिन आया नंबर (Next Result)": int(next_val),
                        "अगले नंबर की फैमिली": str(get_family(next_val))
                    })

    if match_records:
        match_result_df = pd.DataFrame(match_records)
        next_nums_list = match_result_df["अगले दिन आया नंबर (Next Result)"].tolist()
        top_5_next = pd.Series(next_nums_list).value_counts().head(5).to_dict()
        
        st.success(f"🎯 **13 साल के इतिहास में कुल `{len(match_records)}` बार यह पैटर्न मिला है!**")
        st.markdown(f"🔥 **अगले दिन सबसे ज्यादा आए टॉप 5 नंबर:** `{top_5_next}`")
        
        st.write("📋 **ऐतिहासिक मैचों का पूरा रिकॉर्ड (तारीख और रिजल्ट सहित):**")
        st.dataframe(match_result_df, use_container_width=True)
    else:
        st.info("💡 इस चुने हुए मोड में इतिहास में कोई पैटर्न नहीं मिला। कृपया स्लाइडर से दिनों की संख्या (3 या 4) बदलें या सर्च मोड बदलें।")

    st.markdown("---")

    # ================= FORMULA 5 =================
    st.subheader("5️⃣ Continuous Cross-Game Plus/Minus Detector (+/-)")
    flat_results = []
    for idx in range(max(0, len(df)-5), len(df)):
        for c in available_cols:
            if pd.notna(df.loc[idx, c]):
                flat_results.append(int(df.loc[idx, c]))
    
    diff_tracker = []
    for i in range(len(flat_results)-1):
        diff = (flat_results[i+1] - flat_results[i]) % 100
        if diff <= 10 or (100 - diff) <= 10:
            diff_tracker.append(diff)

    top_diffs = pd.Series(diff_tracker).value_counts().head(5).to_dict() if diff_tracker else {}
    st.write(pd.DataFrame([{"एक्टिव +/- अंतराल और फ्रीक्वेंसी": str(top_diffs)}]))

    st.markdown("---")

    # ================= FORMULAS 6 & 7 =================
    st.subheader("6️⃣ & 7️⃣ Multi-Day & Date Digit Sum Engine")
    recent_sums = [get_digit_sum(df.loc[len(df)-1, c]) for c in available_cols if pd.notna(df.loc[len(df)-1, c])]
    st.write(f"📌 **आज का डिजिट सम क्रम:** `{recent_sums}`")
    
    recent_roots = [get_digital_root(df.loc[len(df)-1, c]) for c in available_cols if pd.notna(df.loc[len(df)-1, c])]
    st.info(f"🎯 **डिजिटल रूट (तारीख रिडक्शन):** `{recent_roots}`")

    st.markdown("---")

    # ================= FORMULA 8 =================
    st.subheader("8️⃣ Gap Distance Progression Engine")
    recent_gaps = [get_digit_gap(df.loc[len(df)-1, c]) for c in available_cols if pd.notna(df.loc[len(df)-1, c])]
    st.write(f"📌 **वर्तमान डिजिट गैप सीरीज़ (अंतर):** `{recent_gaps}`")

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
