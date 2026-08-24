import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Monthly Pattern Analyzer", layout="wide")

st.title("📅 चालू महीने का सटीक पैटर्न (13 साल के रिकॉर्ड से मैचिंग)")

# ================= SIDEBAR & FILE UPLOAD =================
st.sidebar.title("📌 फ़ाइल अपलोड")
uploaded_file = st.sidebar.file_uploader("CSV फ़ाइल अपलोड करें", type=["csv"], key="monthly_uploader")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    date_col = 'Date' if 'Date' in df.columns else None
    
    if date_col:
        df['dt_temp'] = pd.to_datetime(df[date_col], errors='coerce')
    
    game_order = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in game_order if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=available_cols, how='all').reset_index(drop=True)

    if "selected_game_m" not in st.session_state or st.session_state["selected_game_m"] not in available_cols:
        st.session_state["selected_game_m"] = available_cols[0]

    st.subheader("🎯 गेम चुनें:")
    cols = st.columns(len(available_cols))
    for idx, col_name in enumerate(available_cols):
        recent_val = df[col_name].dropna().iloc[-1] if not df[col_name].dropna().empty else 0
        with cols[idx]:
            is_active = (st.session_state["selected_game_m"] == col_name)
            btn_label = f"✅ {col_name} ({int(recent_val):02d})" if is_active else f"📌 {col_name} ({int(recent_val):02d})"
            if st.button(btn_label, key=f"btn_m_{col_name}", use_container_width=True):
                st.session_state["selected_game_m"] = col_name

    active_g = st.session_state["selected_game_m"]
    st.markdown("---")

    # चालू महीने के इंडेक्स निकालना
    total_rows = len(df)
    if date_col and 'dt_temp' in df.columns and df['dt_temp'].notna().any():
        latest_dt = df['dt_temp'].dropna().iloc[-1]
        current_month_mask = (df['dt_temp'].dt.year == latest_dt.year) & (df['dt_temp'].dt.month == latest_dt.month)
        curr_month_indices = df[current_month_mask].index.tolist()
    else:
        curr_month_indices = list(range(max(0, total_rows - 31), total_rows))

    # स्लाइडर: लड़ी के दिन
    same_days = st.slider("🎛️ लड़ी के दिन चुनें (सटीक नंबरों के लिए 2 या 3 दिन चुनें):", min_value=1, max_value=5, value=2, key="monthly_same_slider")

    series_vals = df[active_g].tolist()
    records = []

    # चालू महीने की हर तारीख पर लूप
    for idx in curr_month_indices:
        if idx < same_days: continue
        
        curr_date = df.loc[idx, date_col] if date_col else f"Row #{idx}"
        target_seq = series_vals[idx - same_days : idx]
        
        if any(pd.isna(v) for v in target_seq): continue
        target_seq = [int(v) for v in target_seq]
        
        matched_next_results = []
        # पूरे इतिहास में केवल वही लड़ी खोजना (चालू रो को छोड़कर)
        for i in range(total_rows - same_days - 1):
            if i == (idx - same_days): continue
            
            sub_seq = series_vals[i : i + same_days]
            if any(pd.isna(v) for v in sub_seq): continue
            sub_seq = [int(v) for v in sub_seq]
            
            if sub_seq == target_seq:
                if pd.notna(series_vals[i + same_days]):
                    matched_next_results.append(int(series_vals[i + same_days]))
                    
        clean_nums = sorted(list(set(matched_next_results)))
        nums_str = ", ".join([f"{n:02d}" for n in clean_nums]) if clean_nums else "कोई मैच नहीं"
        
        records.append({
            "तारीख": curr_date,
            "चालू महीने की लड़ी (Pattern)": str(target_seq),
            "इतिहास में कुल मैच": len(matched_next_results),
            "यूनिक नंबर": len(clean_nums),
            "कॉपी हेतु नंबर (Next Results)": nums_str
        })

    if records:
        res_df = pd.DataFrame(records)
        res_df = res_df.iloc[::-1].reset_index(drop=True)
        st.dataframe(res_df, use_container_width=True, height=550)
    else:
        st.warning("डेटा उपलब्ध नहीं है।")

else:
    st.info("👈 बाएँ साइडबार से CSV फ़ाइल अपलोड करें।")
