import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Analytics Dashboard", layout="wide")

st.title("📊 Fast Multi-Page Analytics Dashboard")

# ================= HELPER FUNCTIONS =================
RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi_digit(d):
    try:
        return RASHI_MAP.get(int(d), int(d))
    except:
        return 0

def get_family(num):
    try:
        if pd.isna(num): return []
        num = int(num)
        if not (0 <= num <= 99): return []
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
        if not (0 <= num <= 99): return None, None
        return num // 10, num % 10
    except:
        return None, None

def get_haruf_and_rashi_set(num):
    try:
        if pd.isna(num): return set()
        num = int(num)
        if not (0 <= num <= 99): return set()
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
    try:
        diff = (int(val_to) - int(val_from)) % 100
        if diff > 50:
            diff -= 100
        return diff
    except:
        return 0

def check_single_match(mode_id, hist_val, rec_pattern):
    try:
        hist_val = int(hist_val)
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
    except:
        return False
    return False

# ================= FAST CACHED SEARCH ENGINE =================
@st.cache_data
def run_fast_sequence_search(df, g_sel, available_cols, date_col, mode_id, mode_seq_days):
    clean_series = df[g_sel].dropna().astype(int).tolist()
    max_possible_days = len(clean_series)
    
    full_recent_nums = clean_series[-25:] if max_possible_days >= 25 else clean_series
    recent_nums = clean_series[-mode_seq_days:] if max_possible_days >= mode_seq_days else clean_series

    full_patterns = []
    for n in full_recent_nums:
        if mode_id == "1": full_patterns.append(get_haruf_and_rashi_set(n))
        elif mode_id == "2":
            h_i, h_o = get_haruf(n)
            full_patterns.append({h_i, h_o} if h_i is not None else set())
        elif mode_id == "3": full_patterns.append(int(n))
        elif mode_id == "4":
            rev_n = int(f"{int(n):02d}"[::-1])
            full_patterns.append({int(n), rev_n})
        elif mode_id == "5": full_patterns.append(set(get_family(n)))

    recent_patterns = full_patterns[-mode_seq_days:]
    matched_records = []

    for col in available_cols:
        col_vals = df[col].tolist()
        n_vals = len(col_vals)
        for i in range(n_vals - len(recent_nums) - 1):
            sub_seq = col_vals[i : i + len(recent_nums)]
            if any(pd.isna(v) for v in sub_seq): continue
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
                            "Next Result": int(next_val),
                            "अगले नंबर की फैमिली": str(get_family(next_val))
                        })
    return matched_records, recent_nums

# ================= SIDEBAR & NAVIGATION =================
st.sidebar.title("📌 नेविगेशन मेन्यू")
page = st.sidebar.radio(
    "पेज चुनें:", 
    ["1️⃣ सीक्वेंस & हर्फ़ इंजन (F1 - F4)", "2️⃣ क्रॉस-गेम प्रिडिक्टर (F5)", "3️⃣ डिजिट सम & चक्र इंजन (F6 - F9)"]
)

uploaded_file = st.sidebar.file_uploader("CSV फ़ाइल अपलोड करें", type=["csv"], key="dashboard_uploader")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    date_col = 'Date' if 'Date' in df.columns else None
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=available_cols, how='all').reset_index(drop=True)

    # ---------------- PAGE 1 ----------------
    if page == "1️⃣ सीक्वेंस & हर्फ़ इंजन (F1 - F4)":
        st.header("🎯 मास्टर इनपुट & सीक्वेंस पैटर्न (Formulas 1 to 4)")
        c1, c2 = st.columns(2)
        with c1:
            g_sel = st.selectbox("मुख्य गेम चुनें:", available_cols, key="p1_g_sel")
        with c2:
            target_num = st.number_input("टारगेट नंबर दर्ज करें:", 0, 99, 58, key="p1_target")

        # FORMULA 1 & 2
        st.markdown("---")
        st.subheader("1️⃣ & 2️⃣ 24-Hour All-Games Engine")
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
                            if val_int in target_fam: family_hits += 1

            total_ops = len(next_numbers)
            top_nums = pd.Series(next_numbers).value_counts().head(5).to_dict() if next_numbers else {}
            top_in = pd.Series(haruf_in).value_counts().head(3).to_dict() if haruf_in else {}
            top_out = pd.Series(haruf_out).value_counts().head(3).to_dict() if haruf_out else {}
            fam_rate = round((family_hits / total_ops)*100, 2) if total_ops > 0 else 0

            res_df = pd.DataFrame([{
                "कुल ऐतिहासिक मैच": total_matches,
                "24 घंटे मौके": total_ops,
                "टॉप 5 रिपीट नंबर": str(top_nums),
                "फैमिली पासिंग दर (%)": f"{fam_rate}%",
                "टॉप अंदर हर्फ़": str(top_in),
                "टॉप बाहर हर्फ़": str(top_out)
            }])
            st.table(res_df)
        else:
            st.warning("इस गेम में यह नंबर दर्ज नहीं मिला।")

        # FORMULA 3 & 4 (FAST EXPANDERS)
        st.markdown("---")
        st.subheader("3️⃣ & 4️⃣ Sequence Pattern Engine")

        modes = [
            {"id": "1", "name": "1️⃣ हर्फ़ + राशि (Haruf & Rashi)", "key_prefix": "p1_slider_hr"},
            {"id": "2", "name": "2️⃣ केवल हर्फ़ (Direct Haruf - Without Rashi)", "key_prefix": "p1_slider_h"},
            {"id": "3", "name": "3️⃣ सेम टू सेम (Exact Number Match)", "key_prefix": "p1_slider_exact"},
            {"id": "4", "name": "4️⃣ अलट-पलट / पलटी (Direct & Flip/Reverse)", "key_prefix": "p1_slider_flip"},
            {"id": "5", "name": "5️⃣ फैमिली (Full Family Match)", "key_prefix": "p1_slider_fam"}
        ]

        for mode in modes:
            mode_id = mode["id"]
            mode_name = mode["name"]
            key_prefix = mode["key_prefix"]
            
            with st.expander(f"🎯 {mode_name} (खोलने/बंद करने हेतु क्लिक करें 🔽)", expanded=False):
                mode_seq_days = st.slider(f"लड़ी के दिन:", 1, 20, 5, key=f"{key_prefix}_days")

                matched_records, recent_nums = run_fast_sequence_search(df, g_sel, available_cols, date_col, mode_id, mode_seq_days)
                
                st.info(f"📌 `{g_sel}` का हालिया पैटर्न: `{recent_nums}`")

                if matched_records:
                    match_result_df = pd.DataFrame(matched_records)
                    next_nums_list = match_result_df["Next Result"].tolist()
                    top_5_next = pd.Series(next_nums_list).value_counts().head(5).to_dict()
                    
                    st.success(f"✅ **मैच पाए गए: `{len(matched_records)}` बार**")
                    st.markdown(f"🔥 **टॉप 5 नंबर:** `{top_5_next}`")
                    
                    if mode_id == "3":
                        clean_exact_nums = sorted(list(set([int(v) for v in next_nums_list if pd.notna(v)])))
                        exact_box_str = ", ".join([f"{num:02d}" for num in clean_exact_nums])
                        st.markdown(f"📋 **`Next Result` - कुल `{len(clean_exact_nums)}` नंबर (बिना डुप्लीकेट):**")
                        
                        # बड़ा टेक्स्ट एरिया ताकि पूरे 90 नंबर बिना स्क्रॉल के आसानी से दिखें
                        st.text_area("कॉपी हेतु:", value=exact_box_str, height=200, key=f"copy_exact_p1_{mode_id}")

                    elif mode_id == "2":
                        haruf_list = []
                        for num in next_nums_list:
                            h_in, h_out = get_haruf(num)
                            if h_in is not None and h_in not in haruf_list: haruf_list.append(h_in)
                            if h_out is not None and h_out not in haruf_list: haruf_list.append(h_out)
                        haruf_box_str = ", ".join(map(str, sorted(haruf_list)))
                        st.markdown(f"🎲 **सभी हर्फ़ - कुल `{len(haruf_list)}` हर्फ़ (बिना डुप्लीकेट):**")
                        st.text_area("कॉपी हेतु:", value=haruf_box_str, height=100, key=f"copy_haruf_p1_{mode_id}")

                    st.dataframe(match_result_df, use_container_width=True)
                else:
                    st.warning("⚠️ कोई मैच नहीं मिला।")

    # ---------------- PAGE 2 ----------------
    elif page == "2️⃣ क्रॉस-गेम प्रिडिक्टर (F5)":
        st.header("5️⃣ Smart Multi-Day Cross-Game Predictor Engine")
        if len(df) >= 3:
            num_days = st.slider("इतिहास के कितने दिनों का एनालिसिस करना है?", 3, 5, 4, key="p2_f5_slider")
            recent_df = df.tail(num_days).reset_index(drop=True)
            
            st.write(f"📌 **पिछले {num_days} दिनों का डेटा:**")
            st.dataframe(recent_df[['Date'] + available_cols] if 'Date' in recent_df.columns else recent_df[available_cols], use_container_width=True)
            
            all_pair_diffs = []
            for src_g in available_cols:
                for tgt_g in available_cols:
                    if src_g == tgt_g: continue
                    diffs = []
                    for d in range(len(recent_df) - 1):
                        v1, v2 = recent_df.loc[d, src_g], recent_df.loc[d + 1, tgt_g]
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
                        pred_num_str, pred_fam = "N/A", "N/A"
                        if pd.notna(last_src_val):
                            pred_num = (int(last_src_val) + next_diff) % 100
                            pred_num_str = f"{pred_num:02d}"
                            pred_fam = str(get_family(pred_num))
                        
                        all_pair_diffs.append({
                            "गेम कनेक्शन (From ➔ To)": f"{src_g} ➔ {tgt_g}",
                            "पिछले दिनों के डिफरेंस": diff_str,
                            "आज का संभावित डिफरेंस": f"{next_diff:+}",
                            "पैटर्न का प्रकार": pattern_type,
                            "आज का संभावित नंबर": pred_num_str,
                            "फैमिली": pred_fam,
                            "Priority": 1 if (is_same_diff or is_exact_step) else 2
                        })

            diff_matrix_df = pd.DataFrame(all_pair_diffs)
            if not diff_matrix_df.empty:
                diff_matrix_df = diff_matrix_df.sort_values(by=["Priority", "गेम कनेक्शन (From ➔ To)"]).drop(columns=["Priority"])
                st.success("🔥 **6 गेमों के बीच का पूरा डिफरेंस एनालिसिस:**")
                st.dataframe(diff_matrix_df, use_container_width=True)
            else:
                st.warning("पर्याप्त डेटा नहीं मिला।")

    # ---------------- PAGE 3 ----------------
    elif page == "3️⃣ डिजिट सम & चक्र इंजन (F6 - F9)":
        st.header("6️⃣ - 9️⃣ Analytics Engines")
        
        st.subheader("6️⃣ & 7️⃣ Multi-Day & Date Digit Sum Engine")
        recent_sums = [get_digit_sum(df.loc[len(df)-1, c]) for c in available_cols if pd.notna(df.loc[len(df)-1, c])]
        st.write(f"📌 **आज का डिजिट सम क्रम:** `{recent_sums}`")
        recent_roots = [get_digital_root(df.loc[len(df)-1, c]) for c in available_cols if pd.notna(df.loc[len(df)-1, c])]
        st.info(f"🎯 **डिजिटल रूट (तारीख रिडक्शन):** `{recent_roots}`")

        st.markdown("---")
        st.subheader("8️⃣ Gap Distance Progression Engine")
        recent_gaps = [get_digit_gap(df.loc[len(df)-1, c]) for c in available_cols if pd.notna(df.loc[len(df)-1, c])]
        st.write(f"📌 **वर्तमान डिजिट गैप सीरीज़ (अंतर):** `{recent_gaps}`")

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
            st.dataframe(pd.DataFrame(due_items), use_container_width=True)

else:
    st.info("👈 ऐप शुरू करने के लिए बाएँ (Left) साइडबार में अपनी CSV फ़ाइल अपलोड करें।")
