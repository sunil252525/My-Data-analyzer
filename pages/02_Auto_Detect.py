import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Auto-Detect Interactive Dashboard", layout="wide")

st.title("⚡ ऑटो-डिटेक्ट डायनामिक डैशबोर्ड")

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
                next_val = col_vals[i + len(recent_nums)]
                if pd.notna(next_val):
                    rec_date = df.loc[i + len(recent_nums), date_col] if date_col else f"Row #{i + len(recent_nums)}"
                    matched_records.append({
                        "तारीख / रो": rec_date,
                        "गेम का नाम": col,
                        "सटीक लड़ी": str(sub_seq),
                        "Next Result": int(next_val),
                        "फैमिली": str(get_family(next_val))
                    })
    return matched_records, recent_nums

# ================= SIDEBAR & CSV UPLOAD =================
st.sidebar.title("📌 फ़ाइल अपलोड")
uploaded_file = st.sidebar.file_uploader("CSV फ़ाइल अपलोड करें", type=["csv"], key="dashboard_uploader")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    date_col = 'Date' if 'Date' in df.columns else None
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=available_cols, how='all').reset_index(drop=True)

    # State initialization for selected game
    if "selected_game" not in st.session_state:
        st.session_state["selected_game"] = available_cols[0]

    st.subheader("📅 गेम-वाइज़ पिछले 5 दिनों का लेटेस्ट रिकॉर्ड (क्लिक करें):")
    
    # ---------------- DYNAMIC BOXES / CARDS ----------------
    cols = st.columns(len(available_cols))
    
    for idx, col_name in enumerate(available_cols):
        recent_5 = df[col_name].dropna().tail(5).astype(int).tolist()
        recent_str = " - ".join([f"{n:02d}" for n in recent_5])
        
        with cols[idx]:
            # Highlight selected box
            is_active = (st.session_state["selected_game"] == col_name)
            btn_label = f"🎯 {col_name}\n({recent_str})" if not is_active else f"✅ {col_name}\n({recent_str})"
            
            if st.button(btn_label, key=f"btn_{col_name}", use_container_width=True):
                st.session_state["selected_game"] = col_name

    active_g = st.session_state["selected_game"]
    st.markdown("---")
    st.success(f"🔥 वर्तमान में चुना गया गेम: **{active_g}**")

    # ---------------- 3-DAY & 4-DAY SEQUENCE FORMULAS ----------------
    tab_3day, tab_4day = st.tabs(["3️⃣ 3-दिन की लड़ी के फ़ॉर्मूले", "4️⃣ 4-दिन की लड़ी के फ़ॉर्मूले"])

    # --- 3 DAY FORMULAS ---
    with tab_3day:
        st.subheader(f"📊 {active_g} - 3-दिन की लड़ी का पैटर्न एनालिसिस")
        sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(["हर्फ़ + राशि", "केवल हर्फ़", "सेम टू सेम (Exact)", "अलट-पलट / फैमिली"])

        modes_3d = [("1", sub_tab1, "3d_hr"), ("2", sub_tab2, "3d_h"), ("3", sub_tab3, "3d_exact"), ("5", sub_tab4, "3d_fam")]

        for mode_id, t_obj, k_prefix in modes_3d:
            with t_obj:
                matched_records, recent_nums = run_fast_sequence_search(df, active_g, available_cols, date_col, mode_id, 3)
                st.info(f"📌 `{active_g}` का पिछले 3 दिन का पैटर्न: `{recent_nums}`")

                if matched_records:
                    match_df = pd.DataFrame(matched_records)
                    clean_nums = sorted(list(set(match_df["Next Result"].tolist())))
                    box_str = ", ".join([f"{n:02d}" for n in clean_nums])
                    
                    st.success(f"✅ मैच पाए गए: `{len(matched_records)}` बार")
                    st.markdown(f"📋 **Next Result - कुल `{len(clean_nums)}` नंबर (बिना डुप्लीकेट):**")
                    st.text_area("कॉपी हेतु:", value=box_str, height=150, key=f"copy_{k_prefix}_{active_g}")
                    st.dataframe(match_df, use_container_width=True)
                else:
                    st.warning("⚠️ कोई मैच नहीं मिला।")

    # --- 4 DAY FORMULAS ---
    with tab_4day:
        st.subheader(f"📊 {active_g} - 4-दिन की लड़ी का पैटर्न एनालिसिस")
        sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(["हर्फ़ + राशि", "केवल हर्फ़", "सेम टू सेम (Exact)", "अलट-पलट / फैमिली"])

        modes_4d = [("1", sub_tab1, "4d_hr"), ("2", sub_tab2, "4d_h"), ("3", sub_tab3, "4d_exact"), ("5", sub_tab4, "4d_fam")]

        for mode_id, t_obj, k_prefix in modes_4d:
            with t_obj:
                matched_records, recent_nums = run_fast_sequence_search(df, active_g, available_cols, date_col, mode_id, 4)
                st.info(f"📌 `{active_g}` का पिछले 4 दिन का पैटर्न: `{recent_nums}`")

                if matched_records:
                    match_df = pd.DataFrame(matched_records)
                    clean_nums = sorted(list(set(match_df["Next Result"].tolist())))
                    box_str = ", ".join([f"{n:02d}" for n in clean_nums])
                    
                    st.success(f"✅ मैच पाए गए: `{len(matched_records)}` बार")
                    st.markdown(f"📋 **Next Result - कुल `{len(clean_nums)}` नंबर (बिना डुप्लीकेट):**")
                    st.text_area("कॉपी हेतु:", value=box_str, height=150, key=f"copy_{k_prefix}_{active_g}")
                    st.dataframe(match_df, use_container_width=True)
                else:
                    st.warning("⚠️ कोई मैच नहीं मिला।")

else:
    st.info("👈 ऐप शुरू करने के लिए बाएँ साइडबार से CSV फ़ाइल अपलोड करें।")
