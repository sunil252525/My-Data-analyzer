import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Ultra-Fast Analytics Dashboard", layout="wide")

st.title("⚡ Ultra-Fast Analytics Dashboard")

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
def process_sequence_search(df, g_sel, available_cols, date_col, mode_id, mode_seq_days):
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

# ================= SIDEBAR & FILE UPLOAD =================
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

    # PAGE SELECTION USING TABS FOR ZERO-LAG
    main_tab1, main_tab2 = st.tabs(["🎯 लड़ी & पैटर्न इंजन (F1 - F4)", "📊 अन्य एनालिटिक्स इंजन (F5 - F9)"])

    with main_tab1:
        st.header("🎯 मास्टर इनपुट & सीक्वेंस पैटर्न")
        c1, c2 = st.columns(2)
        with c1:
            g_sel = st.selectbox("मुख्य गेम चुनें:", available_cols, key="p1_g_sel")
        with c2:
            target_num = st.number_input("टारगेट नंबर दर्ज करें:", 0, 99, 58, key="p1_target")

        st.markdown("---")
        
        # USE SUB-TABS INSTEAD OF EXPANDERS TO PREVENT LAG
        sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5 = st.tabs([
            "1️⃣ हर्फ़ + राशि", 
            "2️⃣ केवल हर्फ़", 
            "3️⃣ सेम टू सेम", 
            "4️⃣ अलट-पलट", 
            "5️⃣ फैमिली"
        ])

        modes = [
            ("1", sub_tab1, "hr"),
            ("2", sub_tab2, "h"),
            ("3", sub_tab3, "exact"),
            ("4", sub_tab4, "flip"),
            ("5", sub_tab5, "fam")
        ]

        for mode_id, tab_obj, key_pfx in modes:
            with tab_obj:
                mode_seq_days = st.slider("लड़ी के दिन:", 1, 20, 1, key=f"tab_slider_{key_pfx}")
                
                matched_records, recent_nums = process_sequence_search(df, g_sel, available_cols, date_col, mode_id, mode_seq_days)
                
                st.info(f"📌 `{g_sel}` का हालिया पैटर्न: `{recent_nums}`")

                if matched_records:
                    match_result_df = pd.DataFrame(matched_records)
                    next_nums_list = match_result_df["Next Result"].tolist()
                    top_5_next = pd.Series(next_nums_list).value_counts().head(5).to_dict()
                    
                    st.success(f"✅ **मैच पाए गए: `{len(matched_records)}` बार**")
                    st.markdown(f"🔥 **टॉप 5 नंबर:** `{top_5_next}`")
                    
                    clean_exact_nums = sorted(list(set([int(v) for v in next_nums_list if pd.notna(v)])))
                    exact_box_str = ", ".join([f"{num:02d}" for num in clean_exact_nums])
                    
                    st.markdown(f"📋 **Next Result - कुल `{len(clean_exact_nums)}` नंबर (बिना डुप्लीकेट):**")
                    st.text_area("कॉपी हेतु यहाँ क्लिक करें:", value=exact_box_str, height=180, key=f"copy_area_{mode_id}_{key_pfx}")

                    st.dataframe(match_result_df, use_container_width=True)
                else:
                    st.warning("⚠️ कोई मैच नहीं मिला।")

    with main_tab2:
        st.header("📊 क्रॉस-गेम व अन्य एनालिटिक्स")
        st.info("यहाँ आपकी बाकी की फ़ॉर्मूला कैलकुलेशन (F5-F9) तुरंत शो होंगी।")

else:
    st.info("👈 कृपया बाईं ओर से अपनी CSV फ़ाइल अपलोड करें।")
