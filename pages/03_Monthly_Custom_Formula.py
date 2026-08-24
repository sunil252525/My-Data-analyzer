import streamlit as st
import pandas as pd

st.set_page_config(page_title="Family Pattern & Auto-Family Generator", layout="wide")

st.title("👨‍👩‍👧‍👦 फैमिली डिटेक्टर + ऑटो फैमिली जनरेटर")

# ================= HELPER FUNCTIONS =================
RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi_digit(d):
    try: return RASHI_MAP.get(int(d), int(d))
    except: return 0

def get_family(num):
    """किसी भी नंबर की पूरी 8 जोड़ियों वाली फैमिली (अलट-पलट के साथ) जनरेट करता है"""
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

# ================= FAST CACHED FAMILY SEARCH ENGINE =================
@st.cache_data
def run_family_dynamic_search(df, g_sel, available_cols, date_col, mode_seq_days, skip_recent=0):
    clean_series = df[g_sel].dropna().astype(int).tolist()
    if skip_recent > 0:
        clean_series = clean_series[:-skip_recent]
        
    if len(clean_series) < mode_seq_days:
        return [], []

    recent_nums = clean_series[-mode_seq_days:]
    recent_families = [set(get_family(n)) for n in recent_nums]

    matched_records = []
    seen_rows = set()

    for col in available_cols:
        col_vals = df[col].tolist()
        n_vals = len(col_vals)
        
        end_idx_limit = n_vals - len(recent_nums) - skip_recent

        for i in range(end_idx_limit):
            target_idx = i + len(recent_nums)
            
            if (col, target_idx) in seen_rows:
                continue

            sub_seq = col_vals[i : target_idx]
            if any(pd.isna(v) for v in sub_seq): 
                continue
            
            sub_seq = [int(v) for v in sub_seq]
            
            # चेक करें कि क्या ऐतिहासिक नंबर फैमिली मैच कर रहा है
            is_match = True
            for day_idx in range(len(recent_nums)):
                hist_fam = set(get_family(sub_seq[day_idx]))
                if not bool(recent_families[day_idx] & hist_fam):
                    is_match = False
                    break

            if is_match:
                next_val = col_vals[target_idx]
                if pd.notna(next_val):
                    rec_date = df.loc[target_idx, date_col] if date_col and date_col in df.columns else f"Row #{target_idx}"
                    matched_records.append({
                        "तारीख / रो": rec_date,
                        "गेम का नाम": col,
                        "सटीक लड़ी": str(sub_seq),
                        "Next Result": int(next_val)
                    })
                    seen_rows.add((col, target_idx))

    return matched_records, recent_nums


# ================= SIDEBAR & FILE UPLOAD =================
st.sidebar.title("📌 फ़ाइल अपलोड")
uploaded_file = st.sidebar.file_uploader("CSV फ़ाइल अपलोड करें", type=["csv"], key="family_page_uploader")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    date_col = 'Date' if 'Date' in df.columns else None
    
    game_order = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in game_order if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=available_cols, how='all').reset_index(drop=True)

    if "selected_game_fam" not in st.session_state or st.session_state["selected_game_fam"] not in available_cols:
        st.session_state["selected_game_fam"] = available_cols[0]

    st.subheader("📦 गेम चुनें (क्लिक करें):")
    cols = st.columns(len(available_cols))
    for idx, col_name in enumerate(available_cols):
        recent_5 = df[col_name].dropna().tail(5).astype(int).tolist()
        recent_str = " - ".join([f"{n:02d}" for n in recent_5])
        
        with cols[idx]:
            is_active = (st.session_state["selected_game_fam"] == col_name)
            box_label = f"📌 {col_name}\n\n{recent_str}" if not is_active else f"✅ {col_name}\n\n{recent_str}"
            if st.button(box_label, key=f"btn_fam_{col_name}", use_container_width=True):
                st.session_state["selected_game_fam"] = col_name

    active_g = st.session_state["selected_game_fam"]
    st.markdown("---")

    # Slider: Default @ 1 Day
    mode_seq_days = st.slider("🎛️ दिन चुनें (डिफ़ॉल्ट 1 दिन):", min_value=1, max_value=10, value=1, key="fam_slider")

    # Search Logic Call
    matched_records, recent_nums = run_family_dynamic_search(df, active_g, available_cols, date_col, mode_seq_days)

    if recent_nums:
        nums_str = ", ".join([f"{n:02d}" for n in recent_nums])
        st.info(f"📌 **{active_g}** का चुना गया (**{mode_seq_days} दिन**) का फैमिली पैटर्न: `{nums_str}`")

    if matched_records:
        match_df = pd.DataFrame(matched_records)
        
        # 1. अगले दिन आए हुए केवल मूल नंबर (Original Next Results)
        found_nums = sorted(list(set(match_df["Next Result"].tolist())))
        found_box_str = ", ".join([f"{n:02d}" for n in found_nums])
        
        # 2. आए हुए सभी नंबरों की पूरी फैमिली जोड़ियाँ (Generated All Families)
        all_family_nums_set = set()
        for num in found_nums:
            all_family_nums_set.update(get_family(num))
            
        generated_family_nums = sorted(list(all_family_nums_set))
        family_box_str = ", ".join([f"{n:02d}" for n in generated_family_nums])

        st.success(f"✅ कुल मैच मिले: `{len(matched_records)}` बार")
        
        # UI Columns for Dual Displays
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"📋 **1. मूल आए हुए नंबर (Original Next Results) - कुल `{len(found_nums)}`:**")
            st.text_area("कॉपी करें (केवल मूल नंबर):", value=found_box_str, height=150, key=f"txt_orig_{active_g}_{mode_seq_days}")

        with col2:
            st.markdown(f"👑 **2. इन नंबरों की संपूर्ण फैमिली (अलट-पलट के साथ) - कुल `{len(generated_family_nums)}`:**")
            st.text_area("कॉपी करें (पूरी फैमिली जोड़ियाँ):", value=family_box_str, height=150, key=f"txt_generated_fam_{active_g}_{mode_seq_days}")

        st.subheader("📊 सभी फैमिली मिलान का विस्तृत रिकॉर्ड:")
        st.dataframe(match_df, use_container_width=True)
    else:
        st.warning(f"⚠️ `{active_g}` के पैटर्न `{recent_nums}` के लिए कोई फैमिली मैच नहीं मिला।")

else:
    st.info("👈 बाएँ साइडबार से CSV फ़ाइल अपलोड करके शुरू करें।")
    
