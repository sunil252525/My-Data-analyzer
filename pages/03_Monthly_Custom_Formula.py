import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Monthly Single-Day & Family Formula", layout="wide")

st.title("📅 मंथली पैटर्न फ़ॉर्मूला (1-Day Same-to-Same & Family)")

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

# ================= SIDEBAR & FILE UPLOAD =================
st.sidebar.title("📌 फ़ाइल अपलोड")
uploaded_file = st.sidebar.file_uploader("CSV फ़ाइल अपलोड करें", type=["csv"], key="monthly_uploader")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    date_col = 'Date' if 'Date' in df.columns else None
    
    game_order = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in game_order if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=available_cols, how='all').reset_index(drop=True)

    if "selected_game_m" not in st.session_state or st.session_state["selected_game_m"] not in available_cols:
        st.session_state["selected_game_m"] = available_cols[0]

    st.subheader("🎯 गेम चुनें (Delhi Bazaar / SG / FB आदि):")
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

    # ---------------- 2 MAIN SECTIONS TABS ----------------
    tab1, tab2 = st.tabs([
        "1️⃣ सेम-टू-सेम (1-दिन) ऑल-डेट्स रिजल्ट्स", 
        "2️⃣ फैमिली पैटर्न (कस्टम दिन)"
    ])

    # ================= FEATURE 1: 1-DAY SAME TO SAME =================
    with tab1:
        st.subheader(f"📊 `{active_g}` - 1-Day Same-to-Same (हर तारीख/रो का रिजल्ट)")
        
        series_vals = df[active_g].tolist()
        total_rows = len(df)
        
        # टेबल डेटा लिस्ट
        records = []
        for idx in range(1, total_rows):
            curr_date = df.loc[idx, date_col] if date_col else f"Row #{idx}"
            prev_val = series_vals[idx - 1]
            
            if pd.isna(prev_val): continue
            prev_val = int(prev_val)
            
            matched_next_results = []
            for i in range(idx - 1):
                if pd.notna(series_vals[i]) and int(series_vals[i]) == prev_val:
                    if pd.notna(series_vals[i + 1]):
                        matched_next_results.append(int(series_vals[i + 1]))
                        
            clean_nums = sorted(list(set(matched_next_results)))
            nums_str = ", ".join([f"{n:02d}" for n in clean_nums]) if clean_nums else "कोई मैच नहीं"
            
            records.append({
                "तारीख / रो": curr_date,
                "पिछला नंबर": f"{prev_val:02d}",
                "कॉपी वाले कुल नंबर (Count)": len(clean_nums),
                "कॉपी वाले नंबर (Next Results)": nums_str
            })

        if records:
            res_df = pd.DataFrame(records)
            # रिवर्स ऑर्डर (ताजा तारीख सबसे ऊपर)
            res_df = res_df.iloc[::-1].reset_index(drop=True)
            st.dataframe(res_df, use_container_width=True, height=500)
        else:
            st.warning("डेटा उपलब्ध नहीं है।")

    # ================= FEATURE 2: FAMILY PATTERN =================
    with tab2:
        st.subheader(f"👨‍👩‍👧‍👦 `{active_g}` - फैमिली पैटर्न (कस्टम दिन)")
        fam_days = st.slider("🎛️ फैमिली लड़ी के दिन चुनें:", min_value=1, max_value=10, value=3, key="monthly_fam_slider")

        series_vals = df[active_g].tolist()
        total_rows = len(df)
        
        fam_records = []
        for idx in range(fam_days, total_rows):
            curr_date = df.loc[idx, date_col] if date_col else f"Row #{idx}"
            target_seq = series_vals[idx - fam_days : idx]
            
            if any(pd.isna(v) for v in target_seq): continue
            target_seq = [int(v) for v in target_seq]
            
            target_fam_sets = [set(get_family(v)) for v in target_seq]
            
            matched_next_results = []
            for i in range(total_rows - fam_days - 1):
                sub_seq = series_vals[i : i + fam_days]
                if any(pd.isna(v) for v in sub_seq): continue
                sub_seq = [int(v) for v in sub_seq]
                
                is_match = True
                for d in range(fam_days):
                    if not (set(get_family(sub_seq[d])) & target_fam_sets[d]):
                        is_match = False
                        break
                
                if is_match and pd.notna(series_vals[i + fam_days]):
                    matched_next_results.append(int(series_vals[i + fam_days]))
            
            clean_nums = sorted(list(set(matched_next_results)))
            
            all_family_blocked = set()
            for n in clean_nums:
                all_family_blocked.update(get_family(n))
                
            nums_str = ", ".join([f"{n:02d}" for n in clean_nums]) if clean_nums else "कोई मैच नहीं"
            fam_str = ", ".join([f"{n:02d}" for n in sorted(list(all_family_blocked))]) if all_family_blocked else "N/A"

            fam_records.append({
                "तारीख / रो": curr_date,
                "लड़ी पैटर्न": str(target_seq),
                "Next Results (Count)": len(clean_nums),
                "Next Results (कॉपी हेतु)": nums_str,
                "कुल बनी फैमिली जोड़ियाँ": fam_str
            })

        if fam_records:
            fam_df = pd.DataFrame(fam_records)
            fam_df = fam_df.iloc[::-1].reset_index(drop=True)
            st.dataframe(fam_df, use_container_width=True, height=500)
        else:
            st.warning("डेटा उपलब्ध नहीं है।")

else:
    st.info("👈 बाएँ साइडबार से CSV फ़ाइल अपलोड करें।")
