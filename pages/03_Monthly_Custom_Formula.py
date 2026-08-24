import streamlit as st
import pandas as pd

st.set_page_config(page_title="1-Day Same-to-Same Detector", layout="wide")

st.title("🎯 1-डे सेम-टू-सेम (DITTO) डिटेक्टर डैशबोर्ड")

# ================= FAST SEARCH ENGINE (EXACT MATCH ONLY) =================
@st.cache_data
def run_exact_1day_search(df, g_sel, available_cols, date_col, skip_recent=0):
    clean_series = df[g_sel].dropna().astype(int).tolist()
    if skip_recent > 0:
        clean_series = clean_series[:-skip_recent]
        
    if not clean_series:
        return [], None

    # केवल 1 दिन का ताज़ा रिज़ल्ट टारगेट पैटर्न बनेगा
    recent_num = clean_series[-1]

    matched_records = []
    seen_rows = set()

    for col in available_cols:
        col_vals = df[col].tolist()
        n_vals = len(col_vals)
        
        end_idx_limit = n_vals - 1 - skip_recent

        for i in range(end_idx_limit):
            target_idx = i + 1
            
            if (col, target_idx) in seen_rows:
                continue

            hist_val = col_vals[i]
            if pd.isna(hist_val): 
                continue

            # सेम-टू-सेम (Ditto) मैचिंग चेक
            if int(hist_val) == recent_num:
                next_val = col_vals[target_idx]
                if pd.notna(next_val):
                    rec_date = df.loc[target_idx, date_col] if date_col and date_col in df.columns else f"Row #{target_idx}"
                    matched_records.append({
                        "तारीख / रो": rec_date,
                        "गेम का नाम": col,
                        "पिछला नंबर": f"{recent_num:02d}",
                        "Next Result": int(next_val)
                    })
                    seen_rows.add((col, target_idx))

    return matched_records, recent_num


# ================= SIDEBAR & FILE UPLOAD =================
st.sidebar.title("📌 फ़ाइल अपलोड")
uploaded_file = st.sidebar.file_uploader("CSV फ़ाइल अपलोड करें", type=["csv"], key="exact_page_uploader")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    date_col = 'Date' if 'Date' in df.columns else None
    
    game_order = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in game_order if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=available_cols, how='all').reset_index(drop=True)

    if "selected_game_ditto" not in st.session_state or st.session_state["selected_game_ditto"] not in available_cols:
        st.session_state["selected_game_ditto"] = available_cols[0]

    st.subheader("📦 गेम चुनें (क्लिक करें):")
    cols = st.columns(len(available_cols))
    for idx, col_name in enumerate(available_cols):
        recent_5 = df[col_name].dropna().tail(5).astype(int).tolist()
        recent_str = " - ".join([f"{n:02d}" for n in recent_5])
        
        with cols[idx]:
            is_active = (st.session_state["selected_game_ditto"] == col_name)
            box_label = f"📌 {col_name}\n\n{recent_str}" if not is_active else f"✅ {col_name}\n\n{recent_str}"
            if st.button(box_label, key=f"btn_ditto_{col_name}", use_container_width=True):
                st.session_state["selected_game_ditto"] = col_name

    active_g = st.session_state["selected_game_ditto"]
    st.markdown("---")

    # Slide Bar: Default fixed to 1 Day
    mode_seq_days = st.slider("🎛️ दिन चुनें (डिफ़ॉल्ट 1 दिन):", min_value=1, max_value=10, value=1, key="ditto_slider")

    matched_records, recent_num = run_exact_1day_search(df, active_g, available_cols, date_col)

    if recent_num is not None:
        st.info(f"📌 `{active_g}` का ताज़ा (1-Day) रिज़ल्ट नंबर: `{recent_num:02d}`")

    if matched_records:
        match_df = pd.DataFrame(matched_records)
        
        # 1. आए हुए नंबर (Matched / Found Numbers)
        found_nums = sorted(list(set(match_df["Next Result"].tolist())))
        found_box_str = ", ".join([f"{n:02d}" for n in found_nums])
        
        # 2. नहीं आए हुए नंबर (Missing Numbers from 00-99)
        all_100_nums = set(range(100))
        missing_nums = sorted(list(all_100_nums - set(found_nums)))
        missing_box_str = ", ".join([f"{n:02d}" for n in missing_nums])

        st.success(f"✅ कुल मैच मिले: `{len(matched_records)}` बार")
        
        # UI Columns for Copy/Paste Display
        col_f, col_m = st.columns(2)
        
        with col_f:
            st.markdown(f"📋 **1. आए हुए नंबर (Matched / Found) - कुल `{len(found_nums)}`:**")
            st.text_area("कॉपी करें (Found Numbers):", value=found_box_str, height=150, key="txt_found_ditto")

        with col_m:
            st.markdown(f"🚫 **2. छूटे हुए नंबर (Missing Numbers) - कुल `{len(missing_nums)}`:**")
            st.text_area("कॉपी करें (Missing Numbers):", value=missing_box_str, height=150, key="txt_missing_ditto")

        st.subheader("📊 सभी मिलान का विस्तृत रिकॉर्ड:")
        st.dataframe(match_df, use_container_width=True)
    else:
        st.warning("⚠️ कोई मैच नहीं मिला।")

else:
    st.info("👈 बाएँ साइडबार से CSV फ़ाइल अपलोड करके शुरू करें।")
    
