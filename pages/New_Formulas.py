import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="All-in-One Analytics Dashboard", layout="wide")

st.title("📊 All-in-One 9-Formula Dashboard (With Cross-Game Predictor)")

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

    # ================= FORMULA 5 (CROSS-GAME CONTINUOUS CHAIN ENGINE) =================
    st.subheader("5️⃣ All 6-Games Continuous Plus/Minus & Step Predictor Engine")
    
    latest_row = df.iloc[-1]
    prev_row = df.iloc[-2] if len(df) > 1 else None
    
    chain_results = []
    if prev_row is not None:
        for c in available_cols:
            if pd.notna(prev_row[c]):
                chain_results.append((c, int(prev_row[c])))
    for c in available_cols:
        if pd.notna(latest_row[c]):
            chain_results.append((c, int(latest_row[c])))
    
    recent_chain = chain_results[-6:] if len(chain_results) >= 6 else chain_results
    chain_vals = [val for game, val in recent_chain]
    
    st.info(f"📌 **लगातार 6 गेमों की हालिया लड़ी (Chain):** " + " ➔ ".join([f"{g}: `{v:02d}`" for g, v in recent_chain]))

    if len(chain_vals) >= 3:
        diffs = [(chain_vals[i+1] - chain_vals[i]) % 100 for i in range(len(chain_vals)-1)]
        last_game_name, last_val = recent_chain[-1]
        
        st.write(f"📈 **गेम-टू-गेम आपस में अंतर (Cross-Game Differences):** " + " ➔ ".join([f"({d:+})" for d in diffs]))

        predictions = []

        last_diff = diffs[-1]
        same_step_num = (last_val + last_diff) % 100
        predictions.append({
            "पैटर्न का प्रकार (Pattern Step)": f"समान अंतर पैटर्न (Same Diff {last_diff:+})",
            "कैलकुलेशन (Logic)": f"पिछला रिजल्ट ({last_val:02d}) {last_diff:+}",
            "आज आने वाला अगला संभावित नंबर": f"{same_step_num:02d}",
            "फैमिली": str(get_family(same_step_num))
        })

        plus1_num = (last_val + 1) % 100
        predictions.append({
            "पैटर्न का प्रकार (Pattern Step)": "+1 सीधा कदम (+1 Step)",
            "कैलकुलेशन (Logic)": f"पिछला रिजल्ट ({last_val:02d}) + 1",
            "आज आने वाला अगला संभावित नंबर": f"{plus1_num:02d}",
            "फैमिली": str(get_family(plus1_num))
        })

        minus1_num = (last_val - 1) % 100
        predictions.append({
            "पैटर्न का प्रकार (Pattern Step)": "-1 सीधा कदम (-1 Step)",
            "कैलकुलेशन (Logic)": f"पिछला रिजल्ट ({last_val:02d}) - 1",
            "आज आने वाला अगला संभावित नंबर": f"{minus1_num:02d}",
            "फैमिली": str(get_family(minus1_num))
        })

        if len(diffs) >= 2:
            diff_change = diffs[-1] - diffs[-2]
            next_diff = (diffs[-1] + diff_change) % 100
            prog_num = (last_val + next_diff) % 100
            predictions.append({
                "पैटर्न का प्रकार (Pattern Step)": f"अंतर बढ़ता/घटता क्रम (Progression Diff {next_diff:+})",
                "कैलकुलेशन (Logic)": f"पिछला रिजल्ट ({last_val:02d}) {next_diff:+}",
                "आज आने वाला अगला संभावित नंबर": f"{prog_num:02d}",
                "फैमिली": str(get_family(prog_num))
            })

        st.success(f"🎯 **`{last_game_name}` ({last_val:02d}) के बाद आने वाली अगली गेम के संभावित गणितीय नंबर:**")
        st.table(pd.DataFrame(predictions))

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
