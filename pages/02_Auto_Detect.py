import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Auto-Detect & Multi-Formula Dashboard", layout="wide")

st.title("⚡ ऑटो-डिटेक्ट एडवांस डैशबोर्ड")

# ================= HELPER FUNCTIONS =================
RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi_digit(d):
    try: return RASHI_MAP.get(int(d), int(d))
    except: return 0

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
    except: return []

def get_haruf(num):
    try:
        if pd.isna(num): return None, None
        num = int(num)
        if not (0 <= num <= 99): return None, None
        return num // 10, num % 10
    except: return None, None

def get_haruf_and_rashi_set(num):
    try:
        if pd.isna(num): return set()
        num = int(num)
        if not (0 <= num <= 99): return set()
        d1, d2 = num // 10, num % 10
        r1, r2 = get_rashi_digit(d1), get_rashi_digit(d2)
        return {d1, d2, r1, r2}
    except: return set()

def check_single_match(mode_id, hist_val, rec_pattern):
    try:
        hist_val = int(hist_val)
        if mode_id == "1": return bool(rec_pattern & get_haruf_and_rashi_set(hist_val))
        elif mode_id == "2":
            h_i, h_o = get_haruf(hist_val)
            hist_set = {h_i, h_o} if h_i is not None else set()
            return bool(rec_pattern & hist_set)
        elif mode_id == "3": return hist_val == rec_pattern
        elif mode_id == "4": return hist_val in rec_pattern
        elif mode_id == "5": return bool(rec_pattern & set(get_family(hist_val)))
    except: return False
    return False

# ================= FAST CACHED SEARCH ENGINE =================
@st.cache_data
def run_fast_sequence_search(df, g_sel, available_cols, date_col, mode_id, mode_seq_days, skip_recent=0):
    clean_series = df[g_sel].dropna().astype(int).tolist()
    if skip_recent > 0:
        clean_series = clean_series[:-skip_recent]
        
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
        
        end_idx_limit = n_vals - len(recent_nums) - 1
        if skip_recent > 0:
            end_idx_limit -= skip_recent

        for i in range(end_idx_limit):
            sub_seq = col_vals[i : i + len(recent_nums)]
            if any(pd.isna(v) for v in sub_seq): continue
            sub_seq = [int(v) for v in sub_seq]
            
            is_match = True
            for day_idx in range(len(recent_nums)):
                if not check_single_match(mode_id, sub_seq[day_idx], recent_patterns[day_idx]):
                    is_match = False
                    break

            if is_match:
                next_val = col_vals[i + len(recent_nums)]
                if pd.notna(next_val):
                    rec_date = df.loc[i + len(recent_nums), date_col] if date_col else f"Row #{i + len(recent_nums)}"
                    matched_records.append({
                        "तारीख / रो": rec_date,
                        "गेम का नाम": col,
                        "सटीक लड़ी": str(sub_seq),
                        "Next Result": int(next_val)
                    })
    return matched_records, recent_nums

# ================= AUTO 1 TO 20 DAYS CROSSING ENGINE =================
@st.cache_data
def run_auto_20day_haruf_cross(df, active_g, available_cols, date_col, skip_recent=0):
    haruf_counts = {d: 0 for d in range(10)}
    
    for seq_len in range(1, 21):
        for mode_id in ["1", "2", "3", "4", "5"]:
            matched_recs, _ = run_fast_sequence_search(df, active_g, available_cols, date_col, mode_id, seq_len, skip_recent)
            for r in matched_recs:
                val = r["Next Result"]
                hi, ho = get_haruf(val)
                if hi is not None: haruf_counts[hi] += 1
                if ho is not None: haruf_counts[ho] += 1

    top_6_harufs = sorted(haruf_counts.keys(), key=lambda x: haruf_counts[x], reverse=True)[:6]
    top_6_harufs.sort()
    pairs_36 = [f"{h1}{h2}" for h1 in top_6_harufs for h2 in top_6_harufs]
    return top_6_harufs, pairs_36, haruf_counts

# ================= BACKTEST FORMATTING =================
def format_backtest_result(df, active_g, available_cols, date_col, t_offset, label):
    top_6_harufs, pairs_36, _ = run_auto_20day_haruf_cross(df, active_g, available_cols, date_col, skip_recent=t_offset)
    
    if not top_6_harufs:
        return f"**{label}:** पर्याप्त डेटा नहीं"

    clean_series = df[active_g].dropna().astype(int).tolist()
    if len(clean_series) < t_offset:
        return f"**{label}:** रिज़ल्ट उपलब्ध नहीं"
        
    actual_result = clean_series[-t_offset] if t_offset > 0 else "Pending..."
    
    if t_offset > 0:
        actual_str = f"{actual_result:02d}"
        if actual_str in pairs_36:
            status = f"✅ **PASS** (आया: {actual_str})"
        else:
            status = f"❌ **FAIL** (आया: {actual_str})"
    else:
        status = "⏳ **आज का इंतज़ार...**"
        
    crossing_str = "".join(map(str, top_6_harufs))
    return f"**{label}:** हरूफ़ `{crossing_str}` ➔ {status}"


# ================= SIDEBAR & FILE UPLOAD =================
st.sidebar.title("📌 फ़ाइल अपलोड")
uploaded_file = st.sidebar.file_uploader("CSV फ़ाइल अपलोड करें", type=["csv"], key="dashboard_uploader")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    date_col = 'Date' if 'Date' in df.columns else None
    
    game_order = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in game_order if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=available_cols, how='all').reset_index(drop=True)

    if "selected_game" not in st.session_state or st.session_state["selected_game"] not in available_cols:
        st.session_state["selected_game"] = available_cols[0]

    st.subheader("📦 गेम-वाइज़ रिकॉर्ड बॉक्सेज़ (क्लिक करें):")
    
    # ---------------- 6 GRID BOXES ----------------
    cols = st.columns(len(available_cols))
    for idx, col_name in enumerate(available_cols):
        recent_5 = df[col_name].dropna().tail(5).astype(int).tolist()
        recent_str = " - ".join([f"{n:02d}" for n in recent_5])
        
        with cols[idx]:
            is_active = (st.session_state["selected_game"] == col_name)
            box_label = f"📌 {col_name}\n\n{recent_str}" if not is_active else f"✅ {col_name}\n\n{recent_str}"
            if st.button(box_label, key=f"btn_{col_name}", use_container_width=True):
                st.session_state["selected_game"] = col_name

    active_g = st.session_state["selected_game"]
    st.markdown("---")
    
    st.success(f"🎯 ऑटो-सिस्टम एक्टिवेटेड: **{active_g}**")

    # ---------------- MAIN SECTION TABS ----------------
    main_tab1, main_tab2, main_tab3 = st.tabs(["📊 मैनुअल लड़ी पैटर्न", "🤖 ऑटो 6-हरूफ़ (बैकटेस्ट)", "⚡ ऑटो-डिटेक्ट Rare Number 24H"])

    # ================= TAB 1: MANUAL SEQUENCE PATTERNS =================
    with main_tab1:
        mode_seq_days = st.slider("🎛️ मैनुअल लड़ी दिन चुनें:", min_value=1, max_value=20, value=3, key="global_seq_slider")
        sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5 = st.tabs([
            "1️⃣ हर्फ़ + राशि", "2️⃣ केवल हर्फ़", "3️⃣ सेम टू सेम", "4️⃣ अलट-पलट", "5️⃣ फैमिली"
        ])

        modes = [
            ("1", sub_tab1, "hr"), ("2", sub_tab2, "h"), 
            ("3", sub_tab3, "exact"), ("4", sub_tab4, "flip"), ("5", sub_tab5, "fam")
        ]

        for mode_id, t_obj, k_prefix in modes:
            with t_obj:
                matched_records, recent_nums = run_fast_sequence_search(df, active_g, available_cols, date_col, mode_id, mode_seq_days)
                st.info(f"📌 `{active_g}` का पिछले **{mode_seq_days} दिन** का पैटर्न: `{recent_nums}`")

                if matched_records:
                    match_df = pd.DataFrame(matched_records)
                    clean_nums = sorted(list(set(match_df["Next Result"].tolist())))
                    box_str = ", ".join([f"{n:02d}" for n in clean_nums])
                    
                    st.success(f"✅ मैच पाए गए: `{len(matched_records)}` बार")
                    st.markdown(f"📋 **Next Result - कुल `{len(clean_nums)}` नंबर:**")
                    st.text_area("कॉपी हेतु यहाँ क्लिक करें:", value=box_str, height=140, key=f"copy_{k_prefix}_{active_g}_{mode_seq_days}")
                    st.dataframe(match_df, use_container_width=True)
                else:
                    st.warning(f"⚠️ कोई मैच नहीं मिला।")

    # ================= TAB 2: FULL AUTO 6-HARUF & BACKTEST =================
    with main_tab2:
        st.subheader(f"🤖 `{active_g}` - 6-हरूफ़ स्मार्ट क्रॉसिंग (1-20D ऑटो-स्कैन)")
        
        with st.spinner("पिछले 3 दिनों का बैकटेस्ट और आज की क्रॉसिंग जनरेट हो रही है..."):
            bt_t3 = format_backtest_result(df, active_g, available_cols, date_col, 3, "T-3 (तीन दिन पहले)")
            bt_t2 = format_backtest_result(df, active_g, available_cols, date_col, 2, "T-2 (परसों)")
            bt_t1 = format_backtest_result(df, active_g, available_cols, date_col, 1, "T-1 (कल)")
            
            top_6_harufs, pairs_36, haruf_counts = run_auto_20day_haruf_cross(df, active_g, available_cols, date_col, skip_recent=0)

        st.info(f"""
        🕰️ **पिछले 3 दिन का क्रॉसिंग बैकटेस्ट (6x6):**
        * {bt_t3}
        * {bt_t2}
        * {bt_t1}
        """)

        if top_6_harufs:
            crossing_str = "".join(map(str, top_6_harufs))
            pairs_formatted = ", ".join(pairs_36)
            
            st.success(f"🔥 **आज के लिए टॉप 6 हरूफ़ (T-0):** `{crossing_str}`")
            st.markdown("📋 **आज की 36 सॉलिड जोड़ियाँ (6x6 Cross):**")
            st.text_area("36 जोड़ियाँ कॉपी करें:", value=pairs_formatted, height=140, key="copy_auto_crossing_pairs_bt")
            
            st.markdown("📊 **हरूफ़ स्कोर कार्ड:**")
            st.dataframe(pd.DataFrame([haruf_counts]), use_container_width=True)
        else:
            st.warning("क्रॉसिंग जनरेट करने के लिए पर्याप्त डेटा नहीं मिला।")

    # ================= TAB 3: AUTO-DETECT RARE NUMBER 24H SCANNER =================
    with main_tab3:
        st.subheader("⚡ ऑटो-डिटेक्ट रेयर नंबर 24H स्कैनर")
        
        latest_val = df[active_g].dropna().iloc[-1] if not df[active_g].dropna().empty else 20
        auto_detected_num = int(latest_val)
        
        c_target_num, c_btn = st.columns([2, 1])
        with c_target_num:
            scan_target = st.number_input(f"टारगेट नंबर (ऑटो-डिटेक्टेड: `{auto_detected_num:02d}`):", 0, 99, auto_detected_num, key="scan_target_num_auto_24h")
        
        hist_records_24h = []
        direct_hits = []
        family_hits = []
        location_hits = []

        for col in available_cols:
            col_series = df[col].dropna().reset_index(drop=True)
            for idx in range(len(col_series) - 1):
                if int(col_series[idx]) == scan_target:
                    target_row_idx = idx + 1
                    next_found_nums = []

                    if target_row_idx < len(df):
                        for g_col in available_cols:
                            val = df.loc[target_row_idx, g_col]
                            if pd.notna(val):
                                val_int = int(val)
                                next_found_nums.append(val_int)
                                location_hits.append(g_col)

                    for n in next_found_nums:
                        direct_hits.append(n)
                        fam_list = get_family(n)
                        if fam_list:
                            family_hits.append(f"फैमिली {fam_list[0]:02d}")

                    rec_date = df.loc[idx, 'Date'] if 'Date' in df.columns else f"Row #{idx}"
                    unique_next_nums = sorted(list(set(next_found_nums)))
                    
                    hist_records_24h.append({
                        "तारीख / रो": rec_date,
                        "गेम": col,
                        "टारगेट": f"{scan_target:02d}",
                        "अगले नंबर": ", ".join([f"{n:02d}" for n in unique_next_nums])
                    })

        if hist_records_24h:
            st.success(f"🎯 **नंबर `{scan_target:02d}` के 24 घंटे का डेटा (कुल `{len(hist_records_24h)}` मैच):**")
            
            top_direct_series = pd.Series(direct_hits).value_counts()
            top_family_series = pd.Series(family_hits).value_counts()
            top_location_series = pd.Series(location_hits).value_counts()

            best_number = top_direct_series.index[0] if not top_direct_series.empty else "N/A"
            best_number_count = top_direct_series.iloc[0] if not top_direct_series.empty else 0

            best_family = top_family_series.index[0] if not top_family_series.empty else "N/A"
            best_family_count = top_family_series.iloc[0] if not top_family_series.empty else 0

            st.info(f"🏆 **टॉप 24H नंबर:** `{best_number}` ({best_number_count} बार) | **टॉप 24H फैमिली:** `{best_family}` ({best_family_count} बार)")

            col_res1, col_res2, col_res3 = st.columns(3)
            with col_res1:
                st.markdown("🔥 **टॉप 5 नंबर:**")
                st.table(top_direct_series.head(5).rename("पासिंग"))
            with col_res2:
                st.markdown("👑 **टॉप 5 फैमिली:**")
                st.table(top_family_series.head(5).rename("पासिंग"))
            with col_res3:
                st.markdown("📍 **टॉप 5 गेम:**")
                st.table(top_location_series.head(5).rename("पासिंग"))

            st.dataframe(pd.DataFrame(hist_records_24h), use_container_width=True)
        else:
            st.warning(f"नंबर `{scan_target:02d}` का कोई रिकॉर्ड नहीं मिला।")

else:
    st.info("👈 ऐप शुरू करने के लिए बाएँ साइडबार से CSV फ़ाइल अपलोड करें।")
