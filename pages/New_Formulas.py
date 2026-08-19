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
        # ================= TOP SECTION: CURRENT MONTH ONLY DIGIT FREQUENCY =================
    st.markdown("---")
    st.subheader("📊 चालू महीने का अंक/हरूफ़ फ्रीक्वेंसी बोर्ड (Current Month Only)")

    month_df = df.copy()
    current_m_label = "चालू महीना"

    # 1. 13 साल के डेटाबेस में से केवल चालू (लेटेस्ट) महीने का डेटा अलग करना
    if date_col and date_col in month_df.columns:
        try:
            month_df['dt_temp'] = pd.to_datetime(month_df[date_col], errors='coerce')
            valid_dt = month_df['dt_temp'].dropna()
            if not valid_dt.empty:
                latest_m = valid_dt.iloc[-1].month
                latest_y = valid_dt.iloc[-1].year
                # केवल लेटेस्ट महीने और साल की रो (Rows) फ़िल्टर करना
                month_df = month_df[(month_df['dt_temp'].dt.month == latest_m) & (month_df['dt_temp'].dt.year == latest_y)].reset_index(drop=True)
                current_m_label = f"महीना: {int(latest_m)}/{int(latest_y)}"
        except:
            # अगर Date फ़ॉर्मैट में दिक्कत हो तो केवल आखरी 30 दिनों का रिकॉर्ड लेना
            month_df = month_df.tail(30).reset_index(drop=True)
            current_m_label = "चालू महीने का रिकॉर्ड (Last 30 Rows)"
    else:
        # अगर Date का कॉलम ही न हो तो सीधे आखरी 30 दिनों/रो का डेटा लेना
        month_df = month_df.tail(30).reset_index(drop=True)
        current_m_label = "चालू महीने का रिकॉर्ड (हालिया डेटा)"

    st.caption(f"📅 **फ़िल्टर लागू:** 13 साल का पुराना डेटा हटाकर केवल `{current_m_label}` की 6 गेमों का विश्लेषण दिखाया जा रहा है।")

    # 2. 0 से 9 तक के सभी अंकों की केवल इस महीने की गिनती
    digit_counts = {str(d): 0 for d in range(10)}

    for col in available_cols:
        if col in month_df.columns:
            for val in month_df[col].dropna():
                val_str = f"{int(val):02d}"
                for char in val_str:
                    if char in digit_counts:
                        digit_counts[char] += 1

    # 3. 10 मैट्रिक्स डिब्बे (0 से 9 अंक)
    cols = st.columns(10)
    for i in range(10):
        digit_key = str(i)
        count_val = digit_counts[digit_key]
        with cols[i]:
            st.metric(label=f"अंक '{digit_key}'", value=f"{count_val} बार")

    # 4. इस महीने के हॉट और कोल्ड अंक
    sorted_digits = sorted(digit_counts.items(), key=lambda x: x[1], reverse=True)
    hot_digits = ", ".join([f"'{k}' ({v} बार)" for k, v in sorted_digits[:3]])
    cold_digits = ", ".join([f"'{k}' ({v} बार)" for k, v in sorted_digits[-3:]])

    st.info(f"🔥 **इस महीने के सबसे हॉट अंक:** {hot_digits} | 🧊 **इस महीने के ठंडे/कम अंक:** {cold_digits}")

    
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
# ================= FORMULA 10 (6-GAME RARE NUMBER & 2-DAY FOLLOW-UP SCANNER) =================
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

        target_fam = set(get_family(scan_target))

        # पूरे 13 साल के डेटाबेस में स्कैनिंग
        for col in available_cols:
            col_series = df[col].dropna().reset_index(drop=True)
            
            for idx in range(len(col_series) - follow_days):
                if int(col_series[idx]) == scan_target:
                    # अगले 1 या 2 दिन में 6 की 6 गेमों में क्या आया, उसका हिसाब
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

                    # आंकड़े इकट्ठा करना
                    for n in next_found_nums:
                        direct_hits.append(n)
                        family_hits.extend(get_family(n))

                    rec_date = df.loc[idx, 'Date'] if 'Date' in df.columns else f"Row #{idx}"
                    
                    # 6 की 6 गेमों में कौन से नंबर और फैमिली गिरी
                    unique_next_nums = sorted(list(set(next_found_nums)))
                    
                    hist_records.append({
                        "तारीख / रो": rec_date,
                        "जिस गेम में आया": col,
                        "टारगेट नंबर": f"{scan_target:02d}",
                        "अगले 2 दिनों में आए नंबर (सभी 6 गेम)": str(unique_next_nums[:8]) + ("..." if len(unique_next_nums) > 8 else ""),
                        "6 गेमों के रिजल्ट (Game Breakdown)": ", ".join(hit_games[:5]) + "..."
                    })

        if hist_records:
            st.success(f"🎯 **13 साल के रिकॉर्ड में नंबर `{scan_target:02d}` कुल `{len(hist_records)}` बार आया है!**")
            
            # सबसे ज़्यादा आने वाले नंबर और फैमिली का टॉप चार्ट
            top_direct = pd.Series(direct_hits).value_counts().head(5).to_dict()
            top_family = pd.Series(family_hits).value_counts().head(5).to_dict()

            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.markdown(f"🔥 **6 की 6 गेमों में सबसे ज़्यादा बार गिरे 'डायरेक्ट नंबर' (Top Numbers):**")
                st.write(top_direct)
            with col_res2:
                st.markdown(f"💥 **अगले {follow_days} दिनों में सबसे ज़्यादा बार पास होने वाली 'फैमिली':**")
                st.write(top_family)

            st.markdown("📋 **13 साल का पूरा 6-गेम ब्रेकडाउन रिकॉर्ड:**")
            st.dataframe(pd.DataFrame(hist_records), use_container_width=True)
        else:
            st.warning(f"⚠️ 13 साल के इतिहास में नंबर `{scan_target:02d}` का कोई रिकॉर्ड नहीं मिला।")
    # ================= FORMULA 11 (ALL-IN-ONE MASTER WEIGHTED 70-NUMBER ENGINE) =================
    st.markdown("---")
    st.subheader("1️⃣1️⃣ All-in-One Master Weighted Engine (Accurate 20 Main + 50 Support Pairs)")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        f11_game = st.selectbox("11वें फ़ॉर्मूले के लिए मुख्य गेम चुनें:", available_cols, key="f11_select_game")
    with col_m2:
        f11_target = st.number_input("जिस नंबर का 10-फ़ॉर्मूला कॉम्बिनेशन निकालना है (00-99):", 0, 99, target_num, key="f11_select_num")

    if st.button("🚀 सभी 10 फ़ॉर्मूलों का कंबाइंड स्कोर निकालकर 70 नंबर जनरेट करें", key="run_f11_engine"):
        # 00 से 99 तक सभी 100 नंबरों का स्कोर बोर्ड तैयार करना
        scores = {n: 0.0 for n in range(100)}

        # ---------------- 1. HISTORY & FREQUENCY SCORE (F1, F2, F10) ----------------
        hist_matches = df[df[f11_game] == f11_target].index
        next_day_all = []
        haruf_in_list, haruf_out_list = [], []

        for idx in hist_matches:
            if idx + 1 < len(df):
                for col in available_cols:
                    val = df.loc[idx + 1, col]
                    if pd.notna(val):
                        v_int = int(val)
                        next_day_all.append(v_int)
                        hi, ho = get_haruf(v_int)
                        if hi is not None: haruf_in_list.append(hi)
                        if ho is not None: haruf_out_list.append(ho)

        if next_day_all:
            freq = pd.Series(next_day_all).value_counts()
            max_f = freq.max() if not freq.empty else 1
            for num_val, count in freq.items():
                scores[num_val] += (count / max_f) * 30.0  # 30 Points Max

        # ---------------- 2. HARUF, RASHI & TARGET FAMILY SCORE (F1, F2, F3, F4) ----------------
        target_fam = set(get_family(f11_target))
        top_h_in = set(pd.Series(haruf_in_list).value_counts().head(3).index) if haruf_in_list else set()
        top_h_out = set(pd.Series(haruf_out_list).value_counts().head(3).index) if haruf_out_list else set()

        for n in range(100):
            hi, ho = get_haruf(n)
            if hi in top_h_in: scores[n] += 8.0
            if ho in top_h_out: scores[n] += 8.0
            if n in target_fam: scores[n] += 9.0  # Total 25 Points Max

        # ---------------- 3. PLUS / MINUS DIFFERENCE SCORE (F5) ----------------
        if len(df) >= 2:
            last_val = df.loc[len(df)-1, f11_game]
            if pd.notna(last_val):
                last_v = int(last_val)
                # प्रचलित अंतर (+1, -1, +2, -2, +10, -10, +5, -5)
                active_diffs = [-10, -5, -2, -1, 1, 2, 5, 10]
                for d in active_diffs:
                    pred_n = (last_v + d) % 100
                    scores[pred_n] += 2.5  # 20 Points Total Distribution

        # ---------------- 4. DIGIT SUM & DIGITAL ROOT ALIGNMENT (F6, F7, F8) ----------------
        today_roots = [get_digital_root(df.loc[len(df)-1, c]) for c in available_cols if pd.notna(df.loc[len(df)-1, c])]
        today_root_set = set(today_roots)

        for n in range(100):
            if get_digital_root(n) in today_root_set:
                scores[n] += 15.0  # 15 Points Max

        # ---------------- 5. DYNAMIC CYCLE PENDING GAP SCORE (F9) ----------------
        last_idx = len(df) - 1
        for n in range(100):
            idx_list = df[df[f11_game] == n].index.tolist()
            if len(idx_list) >= 2:
                avg_gap = int(np.mean([idx_list[i] - idx_list[i-1] for i in range(1, len(idx_list))]))
                days_since = last_idx - idx_list[-1]
                if abs(days_since - avg_gap) <= 2:
                    scores[n] += 10.0  # 10 Points Max

        # ---------------- 6. SORT & GENERATE ACCURATE 20 MAIN + 50 SUPPORT ----------------
        sorted_numbers = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        main_20 = [item[0] for item in sorted_numbers[:20]]
        support_50 = [item[0] for item in sorted_numbers[20:70]]

        # Formatting with leading zeros (00, 01 ... 99)
        main_20_fmt = [f"{n:02d}" for n in sorted(main_20)]
        support_50_fmt = [f"{n:02d}" for n in sorted(support_50)]

        st.success(f"🎯 **10-फ़ॉर्मूला कंबाइंड स्कोरिंग पूरी हुई!** `{f11_game}` में `{f11_target:02d}` के लिए 70 सबसे सटीक कॉम्बिनेशन तैयार हैं:")

        col_out1, col_out2 = st.columns(2)
        with col_out1:
            st.markdown("### 🔥 **20 मुख्य नंबर (Top Main Pairs - Best Score):**")
            st.code(", ".join(main_20_fmt), language="text")

        with col_out2:
            st.markdown("### 🛡️ **50 सपोर्ट नंबर (Support Pairs - Backup Score):**")
            st.code(", ".join(support_50_fmt), language="text")

        # पारदर्शी स्कोर ब्रेकडाउन की जानकारी
        st.info("💡 **यह 70 नंबर किस तरह फ़िल्टर किए गए हैं?**\n"
                "- 30% अंक: 13 साल की ऐतिहासिक फ्रीक्वेंसी (F1, F2, F10)\n"
                "- 25% अंक: टॉप हर्फ़ व फैमिली मैचिंग (F1-F4)\n"
                "- 20% अंक: प्लस/माइनस डिफ़्रेंस ट्रेंड (F5)\n"
                "- 15% अंक: डिजिट सम व डिजिटल रूट (F6, F7, F8)\n"
                "- 10% अंक: पेंडिंग साइकिल गैप (F9)")
        
