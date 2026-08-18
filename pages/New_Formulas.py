import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="All-in-One Analytics Dashboard", layout="wide")

st.title("📊 All-in-One Analytics Dashboard")

uploaded_file = st.file_uploader("अपनी CSV फ़ाइल यहाँ अपलोड करें", type=["csv"], key="dashboard_uploader")

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

def get_signed_diff(val_from, val_to):
    """प्लस/माइनस अंतर (-50 से +50 की रेंज) निकालता है"""
    diff = (int(val_to) - int(val_from)) % 100
    if diff > 50:
        diff -= 100
    return diff

# ================= MAIN DASHBOARD =================
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    date_col = 'Date' if 'Date' in df.columns else None
    
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    
    df = df.dropna(subset=available_cols, how='all').reset_index(drop=True)

    st.success("✅ डेटाबेस सफलतापूर्वक लोड हो गया!")

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

    # ================= FORMULAS 3 & 4 (ALL-IN-ONE OPEN PATTERN SEARCH ENGINE) =================

    st.subheader("3️⃣ & 4️⃣ All-in-One Sequence Pattern Engine (Individual Controls)")

    # पाँचों पैटर्न मोड की लिस्ट
    modes = [
        {"id": "1", "name": "1️⃣ हर्फ़ + राशि (Haruf & Rashi)", "key_prefix": "slider_hr"},
        {"id": "2", "name": "2️⃣ केवल हर्फ़ (Direct Haruf - Without Rashi)", "key_prefix": "slider_h"},
        {"id": "3", "name": "3️⃣ सेम टू सेम (Exact Number Match)", "key_prefix": "slider_exact"},
        {"id": "4", "name": "4️⃣ अलट-पलट / पलटी (Direct & Flip/Reverse)", "key_prefix": "slider_flip"},
        {"id": "5", "name": "5️⃣ फैमिली (Full Family Match)", "key_prefix": "slider_fam"}
    ]

    # हर मोड के लिए अलग स्लाइडर और पूरा ओपन रिजल्ट
    for mode in modes:
        mode_id = mode["id"]
        mode_name = mode["name"]
        key_prefix = mode["key_prefix"]
        
        st.markdown(f"---")
        st.subheader(f"🎯 {mode_name}")
        
        # 1. हर मोड के ऊपर उसका अपना रेड स्लाइडर (2 से 20 दिनों का)
        mode_seq_days = st.slider(
            f"लड़ी के दिनों की संख्या (Sequence Days) - {mode_name}:", 
            min_value=2, 
            max_value=20, 
            value=5, 
            key=f"{key_prefix}_days"
        )

        clean_series = df[g_sel].dropna().astype(int).tolist()
        recent_nums = clean_series[-mode_seq_days:] if len(clean_series) >= mode_seq_days else clean_series
        
        st.info(f"📌 **`{g_sel}` का हालिया {len(recent_nums)} दिनों का पैटर्न:** `{recent_nums}`")

        # 2. हालिया पैटर्न तैयार करना
        recent_patterns = []
        for n in recent_nums:
            if mode_id == "1":
                recent_patterns.append(get_haruf_and_rashi_set(n))
            elif mode_id == "2":
                h_i, h_o = get_haruf(n)
                recent_patterns.append({h_i, h_o} if h_i is not None else set())
            elif mode_id == "3":
                recent_patterns.append(int(n))
            elif mode_id == "4":
                rev_n = int(f"{int(n):02d}"[::-1])
                recent_patterns.append({int(n), rev_n})
            elif mode_id == "5":
                recent_patterns.append(set(get_family(n)))

        # 3. इतिहास में सर्च करना
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
                    curr_val = sub_seq[day_idx]
                    
                    if mode_id == "1":
                        hist_set = get_haruf_and_rashi_set(curr_val)
                        if not (recent_patterns[day_idx] & hist_set):
                            is_match = False
                            break
                    elif mode_id == "2":
                        h_i, h_o = get_haruf(curr_val)
                        hist_set = {h_i, h_o} if h_i is not None else set()
                        if not (recent_patterns[day_idx] & hist_set):
                            is_match = False
                            break
                    elif mode_id == "3":
                        if curr_val != recent_patterns[day_idx]:
                            is_match = False
                            break
                    elif mode_id == "4":
                        if curr_val not in recent_patterns[day_idx]:
                            is_match = False
                            break
                    elif mode_id == "5":
                        hist_fam = set(get_family(curr_val))
                        if not (recent_patterns[day_idx] & hist_fam):
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

        # 4. परिणाम दिखाना
        if matched_records:
            match_result_df = pd.DataFrame(matched_records)
            next_nums_list = match_result_df["अगले दिन आया रिजल्ट (Next Result)"].tolist()
            top_5_next = pd.Series(next_nums_list).value_counts().head(5).to_dict()
            
            st.success(f"✅ **कुल मैच पाए गए: `{len(matched_records)}` बार**")
            st.markdown(f"🔥 **इसके बाद अगले दिन सबसे ज्यादा बार आए टॉप 5 नंबर:** `{top_5_next}`")
            st.dataframe(match_result_df, use_container_width=True)
        else:
            st.warning("⚠️ इस लड़ी के लिए इतिहास में कोई पैटर्न नहीं मिला। कृपया स्लाइडर से दिनों की संख्या बदलकर देखें।")
    st.subheader("5️⃣ Smart Multi-Day Cross-Game Sequence & Predictor Engine")
    
    if len(df) >= 3:
        num_days = st.slider("इतिहास के कितने दिनों का डिफ़्रेंस एनालिसिस देखना है?", 3, 5, 4, key="f5_slider")
        
        recent_df = df.tail(num_days).reset_index(drop=True)
        
        st.write(f"📌 **पिछले {num_days} दिनों का 6-गेम डेटा बोर्ड:**")
        st.dataframe(recent_df[['Date'] + available_cols] if 'Date' in recent_df.columns else recent_df[available_cols], use_container_width=True)
        
        all_pair_diffs = []
        
        for src_g in available_cols:
            for tgt_g in available_cols:
                if src_g == tgt_g:
                    continue
                
                diffs = []
                for d in range(len(recent_df) - 1):
                    v1 = recent_df.loc[d, src_g]
                    v2 = recent_df.loc[d + 1, tgt_g]
                    if pd.notna(v1) and pd.notna(v2):
                        diffs.append(get_signed_diff(v1, v2))
                
                if len(diffs) >= 2:
                    diff_str = " ➔ ".join([f"{d:+}" for d in diffs])
                    steps = [diffs[i+1] - diffs[i] for i in range(len(diffs)-1)]
                    
                    is_exact_step = len(set(steps)) == 1
                    is_same_diff = len(set(diffs)) == 1
                    
                    if is_same_diff:
                        next_diff = diffs[-1]
                        pattern_type = "🎯 समान अंतर (Same Pattern)"
                    elif is_exact_step:
                        next_diff = diffs[-1] + steps[0]
                        pattern_type = f"📈 लड़ी क्रम (Step {steps[0]:+})"
                    else:
                        avg_step = int(np.round(np.mean(steps))) if steps else 0
                        next_diff = diffs[-1] + avg_step
                        pattern_type = f"📊 ट्रेंड अंतर (Avg Step {avg_step:+})"
                    
                    last_src_val = recent_df.loc[len(recent_df) - 1, src_g]
                    pred_num_str = "N/A"
                    pred_fam = "N/A"
                    
                    if pd.notna(last_src_val):
                        pred_num = (int(last_src_val) + next_diff) % 100
                        pred_num_str = f"{pred_num:02d}"
                        pred_fam = str(get_family(pred_num))
                    
                    all_pair_diffs.append({
                        "गेम कनेक्शन (From ➔ To)": f"{src_g} ➔ {tgt_g}",
                        "पिछले दिनों के डिफ़्रेंस": diff_str,
                        "आज का संभावित डिफ़्रेंस": f"{next_diff:+}",
                        "पैटर्न का प्रकार": pattern_type,
                        "आज का संभावित नंबर": pred_num_str,
                        "फैमिली": pred_fam,
                        "Priority": 1 if (is_same_diff or is_exact_step) else 2
                    })

        diff_matrix_df = pd.DataFrame(all_pair_diffs)
        
        if not diff_matrix_df.empty:
            diff_matrix_df = diff_matrix_df.sort_values(by=["Priority", "गेम कनेक्शन (From ➔ To)"]).drop(columns=["Priority"])
            
            st.success("🔥 **सभी 6 गेमों के बीच पिछले दिनों के डिफ़्रेंस और आने वाले नंबरों का पूरा एनालिसिस:**")
            st.dataframe(diff_matrix_df, use_container_width=True)
        else:
            st.warning("⚠️ डिफ़्रेंस निकालने के लिए पर्याप्त डेटा नहीं मिला।")
    else:
        st.error("डेटाबेस में कम से कम 3 दिनों का डेटा होना आवश्यक है।")

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
# ================= FORMULA 10 (TARGET NUMBER 2-DAY FOLLOW-UP SCANNER) =================
    st.markdown("---")
    st.subheader("🔟 Target Number 2-Day Historical Follow-up & Family Scanner")

    c_target, c_days = st.columns(2)
    with c_target:
        scan_target = st.number_input("जिस नंबर का 13 साल का रिकॉर्ड देखना है (उदा. 20):", 0, 99, 20, key="scan_target_num")
    with c_days:
        follow_days = st.radio("कितने दिनों के अंदर का रिकॉर्ड देखना है?", [1, 2], index=1, key="follow_days_radio")

    if st.button("🔍 13 साल का इतिहास स्कैन करें", key="run_scan_10"):
        hist_records = []
        direct_hits = []
        family_hits = []

        target_fam = set(get_family(scan_target))

        # 13 साल की पूरी CSV डेटाफ़ाइल को स्कैन करना
        for col in available_cols:
            col_series = df[col].dropna().reset_index(drop=True)
            col_dates = df['Date'] if 'Date' in df.columns else None
            
            for idx in range(len(col_series) - follow_days):
                if int(col_series[idx]) == scan_target:
                    # अगले 1 या 2 दिन के रिजल्ट निकालना
                    next_1 = int(col_series[idx + 1])
                    next_2 = int(col_series[idx + 2]) if (follow_days == 2 and idx + 2 < len(col_series)) else None
                    
                    direct_hits.append(next_1)
                    family_hits.extend(get_family(next_1))
                    
                    if next_2 is not None:
                        direct_hits.append(next_2)
                        family_hits.extend(get_family(next_2))

                    rec_date = df.loc[idx, 'Date'] if 'Date' in df.columns else f"Row #{idx}"
                    
                    hist_records.append({
                        "तारीख / रो": rec_date,
                        "गेम": col,
                        "टारगेट नंबर": f"{scan_target:02d}",
                        "1 दिन बाद आया": f"{next_1:02d} (फैमिली: {get_family(next_1)})",
                        "2 दिन बाद आया": f"{next_2:02d} (फैमिली: {get_family(next_2)})" if next_2 is not None else "-"
                    })

        if hist_records:
            st.success(f"🎯 **13 साल के रिकॉर्ड में `{scan_target:02d}` कुल `{len(hist_records)}` बार आया है!**")
            
            # टॉप आने वाले डायरेक्ट नंबर और फैमिली का हिसाब
            top_direct = pd.Series(direct_hits).value_counts().head(5).to_dict()
            top_family = pd.Series(family_hits).value_counts().head(5).to_dict()

            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.markdown(f"🔥 **{follow_days} दिन के अंदर सबसे ज़्यादा बार आए डायरेक्ट नंबर:**")
                st.write(top_direct)
            with col_res2:
                st.markdown(f"💥 **{follow_days} दिन के अंदर सबसे ज़्यादा एक्टिव रहने वाली फैमिली/नंबर:**")
                st.write(top_family)

            st.markdown("📋 **पूरा ऐतिहासिक रिकॉर्ड:**")
            st.dataframe(pd.DataFrame(hist_records), use_container_width=True)
        else:
            st.warning(f"⚠️ इतिहास में नंबर `{scan_target:02d}` का कोई रिकॉर्ड नहीं मिला।")
