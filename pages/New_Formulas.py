import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="All-in-One Analytics Dashboard", layout="wide")

st.title("📊 All-in-One 9-Formula Dashboard (With Active Plus/Minus Sequence)")

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

def get_haruf_and_rashi_set(num):
    try:
        if pd.isna(num): return set()
        num = int(num)
        d1, d2 = num // 10, num % 10
        r1, r2 = get_rashi_digit(d1), get_rashi_digit(d2)
        return {d1, d2, r1, r2}
    except:
        return set()

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

    # ================= FORMULAS 3 & 4 (HARUF & RASHI SEQUENCE ENGINE) =================
    st.subheader("3️⃣ & 4️⃣ 6-Game Haruf & Rashi Pattern Sequence Engine")
    
    seq_days = st.slider("लड़ी के दिनों की संख्या (Sequence Days):", 3, 8, 5, key="seq_slider")

    clean_series = df[g_sel].dropna().astype(int).tolist()
    recent_nums = clean_series[-seq_days:] if len(clean_series) >= seq_days else clean_series
    
    st.info(f"📌 **`{g_sel}` का हालिया {len(recent_nums)} दिनों का पैटर्न:** `{recent_nums}`")

    recent_haruf_sets = [get_haruf_and_rashi_set(n) for n in recent_nums]
    matched_records = []

    for col in available_cols:
        col_vals = df[col].tolist()
        for i in range(len(col_vals) - len(recent_nums) - 1):
            sub_seq = col_vals[i : i + len(recent_nums)]
            if any(pd.isna(v) for v in sub_seq):
                continue
            
            sub_seq = [int(v) for v in sub_seq]
            
            is_match = True
            for day_idx in range(len(recent_nums)):
                hist_haruf_set = get_haruf_and_rashi_set(sub_seq[day_idx])
                if not (recent_haruf_sets[day_idx] & hist_haruf_set):
                    is_match = False
                    break

            if is_match:
                next_val = col_vals[i + len(recent_nums)]
                if pd.notna(next_val):
                    rec_date = df.loc[i + len(recent_nums), date_col] if date_col else f"Row #{i + len(recent_nums)}"
                    matched_records.append({
                        "तारीख / रो (Date/Row)": rec_date,
                        "गेम का नाम": col,
                        "ऐतिहासिक लड़ी": str(sub_seq),
                        "अगले दिन आया रिजल्ट (Next Result)": int(next_val),
                        "अगले नंबर की फैमिली": str(get_family(next_val))
                    })

    if matched_records:
        match_result_df = pd.DataFrame(matched_records)
        next_nums_list = match_result_df["अगले दिन आया रिजल्ट (Next Result)"].tolist()
        top_5_next = pd.Series(next_nums_list).value_counts().head(5).to_dict()
        
        st.success(f"🎯 **13 साल के इतिहास में यह हरूफ़/राशि लड़ी कुल `{len(matched_records)}` बार पाई गई!**")
        st.markdown(f"🔥 **इसके बाद अगले दिन सबसे ज्यादा बार आए टॉप 5 नंबर:** `{top_5_next}`")
        st.dataframe(match_result_df, use_container_width=True)
    else:
        st.warning("⚠️ इस लड़ी के लिए इतिहास में कोई पैटर्न नहीं मिला। कृपया स्लाइडर से दिनों की संख्या को 3 या 4 करके देखें।")

    st.markdown("---")

    # ================= FORMULA 5 (UPDATED PLUS/MINUS SEQUENCE PREDICTOR) =================
    st.subheader("5️⃣ Continuous Cross-Game Plus/Minus Sequence Engine (+/- Predictor)")
    
    # Selected Game Series History
    game_series = df[g_sel].dropna().astype(int).tolist()

    if len(game_series) >= 4:
        last_4 = game_series[-4:]
        diff1 = (last_4[1] - last_4[0]) % 100
        diff2 = (last_4[2] - last_4[1]) % 100
        diff3 = (last_4[3] - last_4[2]) % 100
        
        last_num = last_4[-1]
        
        st.write(f"📌 **`{g_sel}` का हालिया 4 दिनों का ट्रेंड:** `{last_4}`")
        st.write(f"📈 **अंतर (Differences):** `{last_4[0]}` $\\rightarrow$ ({diff1:+}) $\\rightarrow$ `{last_4[1]}` $\\rightarrow$ ({diff2:+}) $\\rightarrow$ `{last_4[2]}` $\\rightarrow$ ({diff3:+}) $\\rightarrow$ `{last_4[3]}`")

        # Logical Next Expected Differences
        possible_next_diffs = []
        
        # 1. Step Progression (e.g. -1, -2 -> Next -3)
        step_diff = diff3 - diff2
        expected_step = (diff3 + step_diff) % 100
        possible_next_diffs.append(("स्टेप सीरीज़ (Step Pattern)", expected_step))
        
        # 2. Same Repeat Difference (e.g. -2, -2 -> Next -2)
        possible_next_diffs.append(("सेम डिफ़्रेंस (Repeat Difference)", diff3))

        # 3. Alternate Difference (e.g. -1, -2, -1 -> Next -2)
        possible_next_diffs.append(("अल्ट्रा डिफ़्रेंस (Alternate Pattern)", diff2))

        # Calculations for Next Potential Numbers
        calc_results = []
        for p_name, p_diff in possible_next_diffs:
            calculated_num = (last_num + p_diff) % 100
            
            # Search History for exact difference sequence match
            hist_matches = []
            for col in available_cols:
                vals = df[col].dropna().astype(int).tolist()
                for idx in range(len(vals) - 4):
                    sub = vals[idx : idx + 4]
                    d1 = (sub[1] - sub[0]) % 100
                    d2 = (sub[2] - sub[1]) % 100
                    d3 = (sub[3] - sub[2]) % 100
                    
                    if (d2 == diff2 and d3 == diff3):
                        next_h = vals[idx + 4]
                        hist_matches.append(next_h)
            
            top_hist = pd.Series(hist_matches).value_counts().head(3).to_dict() if hist_matches else "कोई रिकॉर्ड नहीं"

            calc_results.append({
                "पैटर्न का प्रकार (Pattern Type)": p_name,
                "अपेक्षित +/- (Expected Diff)": f"{p_diff:+}",
                "गणित के अनुसार आज का नंबर": f"{calculated_num:02d}",
                "नंबर की फैमिली": str(get_family(calculated_num)),
                "13 साल में इस डिफ़्रेंस पर सबसे ज्यादा आए नंबर": str(top_hist)
            })

        st.table(pd.DataFrame(calc_results))
    else:
        st.warning("प्लस/माइनस ट्रेंड निकालने के लिए कम से कम 4 दिनों का रिकॉर्ड आवश्यक है।")

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
