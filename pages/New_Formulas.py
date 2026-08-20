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

def check_single_match(mode_id, hist_val, rec_pattern):
    if mode_id == "1":
        return bool(rec_pattern & get_haruf_and_rashi_set(hist_val))
    elif mode_id == "2":
        h_i, h_o = get_haruf(hist_val)
        hist_set = {h_i, h_o} if h_i is not None else set()
        return bool(rec_pattern & hist_set)
    elif mode_id == "3":
        return hist_val == rec_pattern
    elif mode_id == "4":
        return hist_val in rec_pattern
    elif mode_id == "5":
        return bool(rec_pattern & set(get_family(hist_val)))
    return False

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

    # ================= EXACT CURRENT MONTH (AUGUST 2026) DIGIT COUNTER =================
    st.markdown("---")
    st.subheader("📊 8वें महीने (अगस्त 2026) का अंक/हरूफ़ फ्रीक्वेंसी बोर्ड")

    month_df = df.copy()

    if date_col and date_col in month_df.columns:
        month_df['dt_temp'] = pd.to_datetime(month_df[date_col], dayfirst=True, errors='coerce')
        aug_mask = (month_df['dt_temp'].dt.month == 8) & (month_df['dt_temp'].dt.year == 2026)
        filtered_df = month_df[aug_mask].reset_index(drop=True)
        
        if len(filtered_df) > 0:
            month_df = filtered_df
            st.caption("📅 **सटीक फ़िल्टर:** केवल अगस्त 2026 (1 से 19 तारीख तक) का डेटा स्कैन हुआ है।")
        else:
            month_df = month_df.tail(19).reset_index(drop=True)
            st.caption("📅 **फ़िल्टर:** चालू महीने के हालिया 19 दिनों का डेटा स्कैन हुआ है।")
    else:
        month_df = month_df.tail(19).reset_index(drop=True)
        st.caption("📅 **फ़िल्टर:** हालिया 19 दिनों का डेटा:")

    digit_counts = {str(d): 0 for d in range(10)}

    for col in available_cols:
        if col in month_df.columns:
            for val in month_df[col].dropna():
                try:
                    val_int = int(val)
                    val_str = f"{val_int:02d}"
                    for char in val_str:
                        if char in digit_counts:
                            digit_counts[char] += 1
                except:
                    continue

    cols = st.columns(10)
    for i in range(10):
        digit_key = str(i)
        count_val = digit_counts[digit_key]
        with cols[i]:
            st.metric(label=f"अंक '{digit_key}'", value=f"{count_val} बार")

    sorted_digits = sorted(digit_counts.items(), key=lambda x: x[1], reverse=True)
    hot_digits = ", ".join([f"'{k}' ({v} बार)" for k, v in sorted_digits[:3]])
    cold_digits = ", ".join([f"'{k}' ({v} बार)" for k, v in sorted_digits[-3:]])

    st.info(f"🔥 **अगस्त में सबसे ज़्यादा आए अंक:** {hot_digits} | 🧊 **सबसे कम आए अंक:** {cold_digits}")

    # ================= FORMULAS 1 & 2 =================
    st.markdown("---")
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

    # ================= FORMULAS 3 & 4 =================
    st.markdown("---")
    st.subheader("3️⃣ & 4️⃣ All-in-One Sequence Pattern Engine (Non-Overlapping Controls)")

    modes = [
        {"id": "1", "name": "1️⃣ हर्फ़ + राशि (Haruf & Rashi)", "key_prefix": "slider_hr"},
        {"id": "2", "name": "2️⃣ केवल हर्फ़ (Direct Haruf - Without Rashi)", "key_prefix": "slider_h"},
        {"id": "3", "name": "3️⃣ सेम टू सेम (Exact Number Match)", "key_prefix": "slider_exact"},
        {"id": "4", "name": "4️⃣ अलट-पलट / पलटी (Direct & Flip/Reverse)", "key_prefix": "slider_flip"},
        {"id": "5", "name": "5️⃣ फैमिली (Full Family Match)", "key_prefix": "slider_fam"}
    ]

    for mode in modes:
        mode_id = mode["id"]
        mode_name = mode["name"]
        key_prefix = mode["key_prefix"]
        
        st.markdown("---")
        st.subheader(f"🎯 {mode_name}")
        
        mode_seq_days = st.slider(
            f"लड़ी के दिनों की संख्या (Sequence Days) - {mode_name}:", 
            min_value=2, 
            max_value=20, 
            value=5, 
            key=f"{key_prefix}_days"
        )

        clean_series = df[g_sel].dropna().astype(int).tolist()
        max_possible_days = len(clean_series)
        
        full_recent_nums = clean_series[-25:] if max_possible_days >= 25 else clean_series
        recent_nums = clean_series[-mode_seq_days:] if max_possible_days >= mode_seq_days else clean_series
        
        st.info(f"📌 **`{g_sel}` का हालिया {len(recent_nums)} दिनों का पैटर्न:** `{recent_nums}`")

        full_patterns = []
        for n in full_recent_nums:
            if mode_id == "1":
                full_patterns.append(get_haruf_and_rashi_set(n))
            elif mode_id == "2":
                h_i, h_o = get_haruf(n)
                full_patterns.append({h_i, h_o} if h_i is not None else set())
            elif mode_id == "3":
                full_patterns.append(int(n))
            elif mode_id == "4":
                rev_n = int(f"{int(n):02d}"[::-1])
                full_patterns.append({int(n), rev_n})
            elif mode_id == "5":
                full_patterns.append(set(get_family(n)))

        recent_patterns = full_patterns[-mode_seq_days:]

        matched_records = []
        for col in available_cols:
            col_vals = df[col].tolist()
            n_vals = len(col_vals)
            
            for i in range(n_vals - len(recent_nums) - 1):
                sub_seq = col_vals[i : i + len(recent_nums)]
                if any(pd.isna(v) for v in sub_seq):
                    continue
                
                sub_seq = [int(v) for v in sub_seq]
                
                is_match = True
                for day_idx in range(len(recent_nums)):
                    if not check_single_match(mode_id, sub_seq[day_idx], recent_patterns[day_idx]):
                        is_match = False
                        break

                if is_match:
                    has_prior_match = False
                    if i > 0 and len(full_patterns) > len(recent_nums):
                        prev_val = col_vals[i - 1]
                        if pd.notna(prev_val):
                            prior_pattern = full_patterns[-(len(recent_nums) + 1)]
                            if check_single_match(mode_id, int(prev_val), prior_pattern):
                                has_prior_match = True

                    if not has_prior_match:
                        next_val = col_vals[i + len(recent_nums)]
                        if pd.notna(next_val):
                            rec_date = df.loc[i + len(recent_nums), date_col] if date_col else f"Row #{i + len(recent_nums)}"
                            matched_records.append({
                                "तारीख / रो (Date/Row)": rec_date,
                                "गेम का नाम": col,
                                "सटीक लड़ी": str(sub_seq),
                                "अगले दिन आया रिजल्ट (Next Result)": int(next_val),
                                "अगले नंबर की फैमिली": str(get_family(next_val))
                            })

        if matched_records:
            match_result_df = pd.DataFrame(matched_records)
            next_nums_list = match_result_df["अगले दिन आया रिजल्ट (Next Result)"].tolist()
            top_5_next = pd.Series(next_nums_list).value_counts().head(5).to_dict()
            
            st.success(f"✅ **सटीक (Unique) मैच पाए गए: `{len(matched_records)}` बार (कोई डुप्लीकेट/ओवरलैप नहीं)**")
            st.markdown(f"🔥 **इसके बाद अगले दिन सबसे ज्यादा बार आए टॉप 5 नंबर:** `{top_5_next}`")
            st.dataframe(match_result_df, use_container_width=True)
        else:
            st.warning("⚠️ इस सटीक लड़ी के लिए इतिहास में कोई नया/यूनिक पैटर्न नहीं मिला।")

    # ================= FORMULA 5 =================
    st.markdown("---")
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

    # ================= FORMULAS 6 & 7 =================
    st.markdown("---")
    st.subheader("6️⃣ & 7️⃣ Multi-Day & Date Digit Sum Engine")
    recent_sums = [get_digit_sum(df.loc[len(df)-1, c]) for c in available_cols if pd.notna(df.loc[len(df)-1, c])]
    st.write(f"📌 **आज का डिजिट सम क्रम:** `{recent_sums}`")
    
    recent_roots = [get_digital_root(df.loc[len(df)-1, c]) for c in available_cols if pd.notna(df.loc[len(df)-1, c])]
    st.info(f"🎯 **डिजिटल रूट (तारीख रिडक्शन):** `{recent_roots}`")

    # ================= FORMULA 8 =================
    st.markdown("---")
    st.subheader("8️⃣ Gap Distance Progression Engine")
    recent_gaps = [get_digit_gap(df.loc[len(df)-1, c]) for c in available_cols if pd.notna(df.loc[len(df)-1, c])]
    st.write(f"📌 **वर्तमान डिजिट गैप सीरीज़ (अंतर):** `{recent_gaps}`")

    # ================= FORMULA 9 =================
    st.markdown("---")
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

    # ================= FORMULA 10 =================
    st.markdown("---")
    st.subheader("🔟 Target & Rare Number 2-Day Cross-Game Family Scanner")

    c_target, c_days = st.columns(2)
    with c_target:
        scan_target = st.number_input("जिस रेयर/टारगेट नंबर का 13 साल का रिकॉर्ड चेक करना है (उदा. 20, 34, 35):", 0, 99, 20, key="scan_target_num")
    with c_days:
        follow_days = st.radio("कितने दिनों के अंदर का ट्रैक रिकॉर्ड देखना है?", [1, 2], index=1, key="follow_days_radio")

    if st.button("🔍 13 साल का इतिहास स्कैन करें", key="run_scan_10"):
        hist_records = []
        direct_hits = []
        family_hits = []
        location_hits = []
        fam_location_dict = {}

        for col in available_cols:
            col_series = df[col].dropna().reset_index(drop=True)
            
            for idx in range(len(col_series) - follow_days):
                if int(col_series[idx]) == scan_target:
                    next_found_nums = []
                    hit_games = []

                    for day_offset in range(1, follow_days + 1):
                        target_row_idx = idx + day_offset
                        if target_row_idx < len(df):
                            for g_col in available_cols:
                                val = df.loc[target_row_idx, g_col]
                                if pd.notna(val):
                                    val_int = int(val)
                                    next_found_nums.append(val_int)
                                    hit_games.append(f"{g_col} (D+{day_offset}): {val_int:02d}")
                                    
                                    # लोकेशन और फैमिली का ट्रैक रखना
                                    location_hits.append(g_col)
                                    fam_list = get_family(val_int)
                                    if fam_list:
                                        fam_name = f"फैमिली {fam_list[0]:02d} ({fam_list})"
                                        if fam_name not in fam_location_dict:
                                            fam_location_dict[fam_name] = {}
                                        fam_location_dict[fam_name][g_col] = fam_location_dict[fam_name].get(g_col, 0) + 1

                    for n in next_found_nums:
                        direct_hits.append(n)
                        fam_list = get_family(n)
                        if fam_list:
                            family_hits.append(f"फैमिली {fam_list[0]:02d} ({fam_list})")

                    rec_date = df.loc[idx, 'Date'] if 'Date' in df.columns else f"Row #{idx}"
                    unique_next_nums = sorted(list(set(next_found_nums)))
                    
                    hist_records.append({
                        "तारीख / रो": rec_date,
                        "जिस गेम में आया": col,
                        "टारगेट नंबर": f"{scan_target:02d}",
                        "अगले दिनों में आए नंबर (सभी 6 गेम)": str(unique_next_nums[:8]) + ("..." if len(unique_next_nums) > 8 else ""),
                        "6 गेमों के रिजल्ट (Game Breakdown)": ", ".join(hit_games[:5]) + "..."
                    })

        if hist_records:
            st.success(f"🎯 **13 साल के रिकॉर्ड में नंबर `{scan_target:02d}` कुल `{len(hist_records)}` बार आया है!**")
            
            top_direct_series = pd.Series(direct_hits).value_counts()
            top_family_series = pd.Series(family_hits).value_counts()
            top_location_series = pd.Series(location_hits).value_counts()

            best_number = top_direct_series.index[0] if not top_direct_series.empty else "N/A"
            best_number_count = top_direct_series.iloc[0] if not top_direct_series.empty else 0

            best_family = top_family_series.index[0] if not top_family_series.empty else "N/A"
            best_family_count = top_family_series.iloc[0] if not top_family_series.empty else 0

            best_location = top_location_series.index[0] if not top_location_series.empty else "N/A"
            best_location_count = top_location_series.iloc[0] if not top_location_series.empty else 0

            # साफ़ मुख्य परिणाम हाइलाइट बॉक्स
            st.info(f"""
            🏆 **मुख्य निष्कर्ष (Summary):**
            * 💥 **सबसे ज़्यादा बार आने वाला सिंगल नंबर:** `{best_number:02d}` (कुल **{best_number_count}** बार)
            * 👑 **सबसे ज़्यादा पास होने वाली फैमिली:** `{best_family}` (कुल **{best_family_count}** बार)
            * 📍 **सबसे ज़्यादा पासिंग देने वाली लोकेशन/गेम:** `{best_location}` (कुल **{best_location_count}** पासिंग)
            """)

            col_res1, col_res2, col_res3 = st.columns(3)
            with col_res1:
                st.markdown("🔥 **टॉप 5 सिंगल नंबर:**")
                st.table(top_direct_series.head(5).rename("बार आया"))
            with col_res2:
                st.markdown("💥 **टॉप 5 फैमिली:**")
                st.table(top_family_series.head(5).rename("बार पास हुई"))
            with col_res3:
                st.markdown("📍 **गेम/लोकेशन अनुसार कुल पासिंग:**")
                st.table(top_location_series.rename("कुल हिट्स"))

            # फैमिली अनुसार लोकेशन का ब्रेकडाउन टेबल
            fam_loc_rows = []
            for fam_name, loc_counts in fam_location_dict.items():
                total_hits = sum(loc_counts.values())
                loc_summary = ", ".join([f"{loc}: {cnt} बार" for loc, cnt in sorted(loc_counts.items(), key=lambda x: x[1], reverse=True)])
                fam_loc_rows.append({
                    "फैमिली": fam_name,
                    "कुल पासिंग": total_hits,
                    "किस-किस लोकेशन पर कितनी बार आई (Location Breakdown)": loc_summary
                })
            
            fam_loc_df = pd.DataFrame(fam_loc_rows).sort_values(by="कुल पासिंग", ascending=False).reset_index(drop=True)

            st.markdown("📊 **फैमिली अनुसार लोकेशन का ब्रेकडाउन (किस गेम में कितनी बार पास हुई):**")
            st.dataframe(fam_loc_df, use_container_width=True)

            st.markdown("📋 **13 साल का पूरा ब्रेकडाउन रिकॉर्ड:**")
            st.dataframe(pd.DataFrame(hist_records), use_container_width=True)
        else:
            st.warning(f"⚠️ 13 साल के इतिहास में नंबर `{scan_target:02d}` का कोई रिकॉर्ड नहीं मिला।")
            # ================= FORMULA 11 =================
    st.markdown("---")
    st.subheader("1️⃣1️⃣ Time-Frame Cycle & Repeat Guarantee Engine (1, 2, 3, 4 महीने का गैप फ़िल्टर)")

    timeframe_option = st.selectbox(
        "समय सीमा (Cycle Window) चुनें:",
        ["1 महीना (30 दिन)", "2 महीने (60 दिन)", "3 महीने (90 दिन)", "4 महीने (120 दिन)"],
        index=1,
        key="f11_tf_select"
    )

    days_map = {
        "1 महीना (30 दिन)": 30,
        "2 महीने (60 दिन)": 60,
        "3 महीने (90 दिन)": 90,
        "4 महीने (120 दिन)": 120
    }
    target_days = days_map[timeframe_option]

    detected_date_col = None
    for c in df.columns:
        if any(term in str(c).lower() for term in ['date', 'dt', 'tarikh', 'tariq', 'time', 'दिन', 'तारीख']):
            detected_date_col = c
            break

    if detected_date_col is None and date_col and date_col in df.columns:
        detected_date_col = date_col

    temp_df = df.copy()
    has_valid_dates = False

    if detected_date_col:
        temp_df['dt_parsed'] = pd.to_datetime(temp_df[detected_date_col], dayfirst=True, errors='coerce')
        temp_df = temp_df.dropna(subset=['dt_parsed']).sort_values('dt_parsed').reset_index(drop=True)
        if len(temp_df) > 0:
            has_valid_dates = True

    f11_summary = []
    detailed_tables = {}

    for col in available_cols:
        col_res = []
        
        for num in range(100):
            if has_valid_dates:
                num_rows = temp_df[temp_df[col] == num]
                dates = num_rows['dt_parsed'].tolist()
                
                if len(dates) >= 2:
                    gaps = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
                    last_gap = (temp_df['dt_parsed'].max() - dates[-1]).days
                    max_gap = max(gaps)
                    passed_within_target = sum(1 for g in gaps if g <= target_days)
                    total_gaps = len(gaps)
                    pass_rate = round((passed_within_target / total_gaps) * 100, 1) if total_gaps > 0 else 0
                    
                    col_res.append({
                        "नंबर": f"{num:02d}",
                        "13 साल में अधिकतम गैप (दिन)": max_gap,
                        f"तय {target_days} दिनों में आने की दर (%)": pass_rate,
                        "वर्तमान पेंडिंग (दिन)": last_gap,
                        "कुल बार आया": len(dates),
                        "is_perfect": max_gap <= target_days
                    })
            else:
                num_indices = temp_df[temp_df[col] == num].index.tolist()
                if len(num_indices) >= 2:
                    gaps = [num_indices[i] - num_indices[i-1] for i in range(1, len(num_indices))]
                    last_gap = len(temp_df) - 1 - num_indices[-1]
                    max_gap = max(gaps)
                    passed_within_target = sum(1 for g in gaps if g <= target_days)
                    total_gaps = len(gaps)
                    pass_rate = round((passed_within_target / total_gaps) * 100, 1) if total_gaps > 0 else 0
                    
                    col_res.append({
                        "नंबर": f"{num:02d}",
                        "13 साल में अधिकतम गैप (दिन/रो)": max_gap,
                        f"तय {target_days} दिनों में आने की दर (%)": pass_rate,
                        "वर्तमान पेंडिंग (दिन/रो)": last_gap,
                        "कुल बार आया": len(num_indices),
                        "is_perfect": max_gap <= target_days
                    })

        if col_res:
            col_res_df = pd.DataFrame(col_res)
            col_res_df = col_res_df.sort_values(by=[f"तय {target_days} दिनों में आने की दर (%)", "13 साल में अधिकतम गैप (दिन)" if has_valid_dates else "13 साल में अधिकतम गैप (दिन/रो)"], ascending=[False, True])
            
            detailed_tables[col] = col_res_df
            top_best = col_res_df.iloc[0]
            perfect_nums = col_res_df[col_res_df['is_perfect']]['नंबर'].tolist()
            
            f11_summary.append({
                "लोकेशन / गेम": col,
                f"🏆 #1 सबसे गारंटेड नंबर (हर {target_days} दिन)": top_best['नंबर'],
                "13 साल में सबसे लंबा गैप": f"{top_best['13 साल में अधिकतम गैप (दिन)' if has_valid_dates else '13 साल में अधिकतम गैप (दिन/रो)']} दिन",
                "सफलता दर (%)": f"{top_best[f'तय {target_days} दिनों में आने की दर (%)']}%",
                f"100% गारंटेड नंबर (जो कभी {target_days} दिन से ऊपर नहीं गए)": ", ".join(perfect_nums) if perfect_nums else "कोई नहीं (टॉप पासिंग रेट देखें)"
            })

    if f11_summary:
        st.success(f"📊 **{timeframe_option} के गैप एनालिसिस के आधार पर सबसे भरोसेमंद नंबर:**")
        st.dataframe(pd.DataFrame(f11_summary), use_container_width=True)

        st.markdown("---")
        st.subheader("🔍 हर लोकेशन के लिए सभी 100 नंबरों की विस्तृत सूची (Ranked Table)")
        selected_loc = st.selectbox("लोकेशन / गेम चुनें:", available_cols, key="f11_loc_detail")
        if selected_loc in detailed_tables:
            st.dataframe(detailed_tables[selected_loc].drop(columns=['is_perfect']), use_container_width=True)
    else:
        st.warning("⚠️ गैप एनालिसिस निकालने के लिए पर्याप्त डेटा नहीं मिला।")
# ================= FORMULA 12 =================
    st.markdown("---")
    st.subheader("1️⃣2️⃣ Top Single, Main 20 & Top 70 Numbers Engine")

    summary_data = []

    for col in available_cols:
        vals = df[col].dropna().astype(int).tolist()
        valid_vals = [x for x in vals if 0 <= x <= 99]
        
        if valid_vals:
            counts = pd.Series(valid_vals).value_counts()
            
            # 1. #1 सबसे हॉट सिंगल नंबर
            top_1_single = counts.index[0]
            top_1_count = counts.iloc[0]
            
            # 2. टॉप 20 मेन नंबर
            top_20_main = counts.head(20).index.tolist()
            
            # 3. कुल टॉप 70 नंबर
            top_70 = counts.head(70).index.tolist()
            
            # 13 साल की ऐतिहासिक पासिंग दर (%)
            passed_count = sum(counts.head(70))
            coverage_pct = round((passed_count / len(valid_vals)) * 100, 1)

            summary_data.append({
                "लोकेशन / गेम": col,
                "👑 #1 सबसे हॉट सिंगल नंबर": f"{top_1_single:02d} ({top_1_count} बार)",
                "🔥 टॉप 20 मेन नंबर": ", ".join([f"{n:02d}" for n in top_20_main]),
                "📊 70 नंबरों की ऐतिहासिक पासिंग (%)": f"{coverage_pct}%",
                "📋 बाकी 50 सपोर्ट नंबर": ", ".join([f"{n:02d}" for n in top_70[20:]])
            })

    if summary_data:
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
    else:
        st.warning("⚠️ विश्लेषण के लिए डेटा उपलब्ध नहीं है।")
# ================= FORMULA 13 =================
    st.markdown("---")
    st.subheader("1️⃣3️⃣ Premium Selected Numbers Engine (Formulas 3 & 4 Combined)")

    summary_data_13 = []

    for col in available_cols:
        vals = df[col].dropna().astype(int).tolist()
        valid_vals = [x for x in vals if 0 <= x <= 99]
        
        if len(valid_vals) >= 5:
            # 1. फ़ॉर्मूला 3/5 लॉजिक: सबसे ज़्यादा बार आने वाले नंबरों का स्कोर
            freq_counts = pd.Series(valid_vals).value_counts()
            
            # 2. फ़ॉर्मूला 4 लॉजिक: पिछले रिज़ल्ट के बाद अगले 2 दिनों में सबसे ज़्यादा बार आने वाले फ़ॉलो-अप नंबर
            last_num = valid_vals[-1]  # सबसे हाल का रिज़ल्ट
            follow_up_nums = []
            
            for i in range(len(valid_vals) - 2):
                if valid_vals[i] == last_num:
                    follow_up_nums.append(valid_vals[i + 1])
                    follow_up_nums.append(valid_vals[i + 2])
            
            follow_counts = pd.Series(follow_up_nums).value_counts() if follow_up_nums else pd.Series(dtype=int)
            
            # दोनों फ़ॉर्मूलों का संयुक्त स्कोर (Combined Score)
            combined_scores = {n: 0 for n in range(100)}
            
            for n in range(100):
                # फ़्रीक्वेंसी स्कोर
                if n in freq_counts:
                    combined_scores[n] += freq_counts[n] * 1
                # फ़ॉलो-अप स्कोर (3-4 पैटर्न वेटेज)
                if n in follow_counts:
                    combined_scores[n] += follow_counts[n] * 3

            # स्कोर के अनुसार रैंकिंग
            ranked_nums = sorted(combined_scores.keys(), key=lambda x: combined_scores[x], reverse=True)
            
            # सबसे ख़ास फ़िल्टर्ड नंबर
            top_1_special = ranked_nums[0]
            top_20_main = ranked_nums[:20]
            top_70_total = ranked_nums[:70]
            
            summary_data_13.append({
                "लोकेशन / गेम": col,
                "👑 #1 सबसे ख़ास सिंगल नंबर": f"{top_1_special:02d}",
                "🔥 20 सबसे ख़ास मेन नंबर": ", ".join([f"{n:02d}" for n in top_20_main]),
                "📋 बाकी ख़ास सपोर्ट नंबर (कुल 70)": ", ".join([f"{n:02d}" for n in top_70_total[20:]])
            })

    if summary_data_13:
        st.dataframe(pd.DataFrame(summary_data_13), use_container_width=True)
    else:
        st.warning("⚠️ विश्लेषण के लिए डेटा उपलब्ध नहीं है।")
# ================= FORMULA 14 =================
    st.markdown("---")
    st.subheader("1️⃣4️⃣ Top 6 Haruf Crossing Engine (Formulas 3 & 4 Combined)")

    crossing_summary = []

    for col in available_cols:
        vals = df[col].dropna().astype(int).tolist()
        valid_vals = [x for x in vals if 0 <= x <= 99]
        
        if len(valid_vals) >= 5:
            last_num = valid_vals[-1]  # ताज़ा रिज़ल्ट
            
            # 1. फ़ॉर्मूला 3 लॉजिक: पूरे इतिहास में हरूफ़ की फ़्रीक्वेंसी (1 पॉइंट)
            haruf_scores = {d: 0 for d in range(10)}
            for num in valid_vals:
                haruf_scores[num // 10] += 1  # अंदर का हरूफ़
                haruf_scores[num % 10] += 1   # बाहर का हरूफ़

            # 2. फ़ॉर्मूला 4 लॉजिक: ताज़ा रिज़ल्ट के बाद अगले 2 दिनों में आए फ़ॉलो-अप हरूफ़
            follow_up_harufs = []
            for i in range(len(valid_vals) - 2):
                if valid_vals[i] == last_num:
                    f1 = valid_vals[i + 1]
                    f2 = valid_vals[i + 2]
                    follow_up_harufs.extend([f1 // 10, f1 % 10, f2 // 10, f2 % 10])

            # फ़ॉलो-अप हरूफ़ को 3 गुना ज़्यादा वज़न देना (+3 पॉइंट्स)
            for h in follow_up_harufs:
                haruf_scores[h] += 3

            # सबसे ज़्यादा स्कोर वाले टॉप 6 हरूफ़ चुनना
            top_6_harufs = sorted(haruf_scores.keys(), key=lambda x: haruf_scores[x], reverse=True)[:6]
            top_6_harufs.sort()  # बढ़ते क्रम में लगाने के लिए
            
            crossing_haruf_str = ", ".join(map(str, top_6_harufs))
            
            crossing_summary.append({
                "लोकेशन / गेम": col,
                "🎯 ताज़ा रिज़ल्ट": f"{last_num:02d}",
                "🔥 6 हरूफ़ की ख़ास क्रॉसिंग": crossing_haruf_str,
                "👑 टॉप 3 मेन हरूफ़": ", ".join(map(str, top_6_harufs[:3])),
                "💡 कुल जोड़ियाँ": "36 जोड़ियाँ (6x6)"
            })

    if crossing_summary:
        st.dataframe(pd.DataFrame(crossing_summary), use_container_width=True)
    else:
        st.warning("⚠️ विश्लेषण के लिए पर्याप्त डेटा नहीं मिला।")
# ================= FORMULA 15 =================
    st.markdown("---")
    st.subheader("1️⃣5️⃣ 3-Day Backtest & Crossing History Tracker (Formulas 3 & 4)")

    summary_3days_f15 = []

    for col in available_cols:
        vals = df[col].dropna().astype(int).tolist()
        date_list = df['Date'].tolist() if 'Date' in df.columns else [f"Row #{i}" for i in range(len(df))]
        
        if len(vals) >= 8:
            row_data = {"लोकेशन / गेम": col}
            pass_count = 0  # पिछले 3 दिनों की कुल पासिंग गिनती

            # पिछले 3 दिनों का बैकटेस्ट (3 दिन पहले, 2 दिन पहले, 1 दिन पहले)
            for offset in [3, 2, 1]:
                target_idx = len(vals) - offset
                
                if target_idx >= 5:
                    day_date = date_list[target_idx] if target_idx < len(date_list) else f"T-{offset}"
                    actual_result = vals[target_idx]
                    
                    # उस दिन के ठीक पहले तक का इतिहास
                    past_vals = vals[:target_idx]
                    last_trigger_num = past_vals[-1]
                    
                    # 1. फ़ॉर्मूला 3 लॉजिक: इतिहास में हरूफ़ की ओवरऑल फ़्रीक्वेंसी (+1 पॉइंट)
                    haruf_scores = {d: 0 for d in range(10)}
                    for num in past_vals:
                        haruf_scores[num // 10] += 1
                        haruf_scores[num % 10] += 1

                    # 2. फ़ॉर्मूला 4 लॉजिक: लास्ट रिज़ल्ट के फ़ॉलो-अप हरूफ़ (+3 पॉइंट्स)
                    follow_up_harufs = []
                    for i in range(len(past_vals) - 2):
                        if past_vals[i] == last_trigger_num:
                            f1 = past_vals[i + 1]
                            f2 = past_vals[i + 2]
                            follow_up_harufs.extend([f1 // 10, f1 % 10, f2 // 10, f2 % 10])

                    for h in follow_up_harufs:
                        haruf_scores[h] += 3

                    # टॉप 6 हरूफ़ चुनना
                    top_6 = sorted(haruf_scores.keys(), key=lambda x: haruf_scores[x], reverse=True)[:6]
                    top_6.sort()
                    crossing_str = "".join(map(str, top_6))

                    # पास/फेल चेक (अंदर और बाहर दोनों हरूफ़ क्रॉसिंग में होने चाहिए)
                    d1, d2 = actual_result // 10, actual_result % 10
                    is_pass = (d1 in top_6) and (d2 in top_6)
                    
                    status_tag = "✅ पास" if is_pass else "❌ फेल"
                    if is_pass:
                        pass_count += 1

                    # तारीख़ अनुसार कॉलम फ़ॉर्मैटिंग
                    col_header = f"📅 {day_date}"
                    row_data[col_header] = f"🎯 {actual_result:02d} | 🎲 ({crossing_str}) | {status_tag}"

            row_data["📊 3 दिन का स्कोर"] = f"{pass_count}/3 पास"
            summary_3days_f15.append(row_data)

    if summary_3days_f15:
        st.dataframe(pd.DataFrame(summary_3days_f15), use_container_width=True)
    else:
        st.warning("⚠️ बैकटेस्टिंग के लिए पर्याप्त डेटा उपलब्ध नहीं है।")
