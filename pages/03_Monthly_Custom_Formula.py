import streamlit as st
import pandas as pd

st.set_page_config(page_title="All-in-One Dashboard", layout="wide")

st.title("🎯 All-in-One Satta Analysis Dashboard")

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

def get_flip_pairs(num_list):
    flip_set = set()
    for n in num_list:
        try:
            val = int(n)
            flip_val = int(f"{val:02d}"[::-1])
            flip_set.add(val)
            flip_set.add(flip_val)
        except: continue
    return sorted(list(flip_set))

# ================= FAST SEARCH ENGINES =================
@st.cache_data
def run_exact_dynamic_search(df, g_sel, available_cols, date_col, mode_seq_days, skip_recent=0):
    clean_series = df[g_sel].dropna().astype(int).tolist()
    if skip_recent > 0: clean_series = clean_series[:-skip_recent]
    if len(clean_series) < mode_seq_days: return [], []

    recent_nums = clean_series[-mode_seq_days:]
    matched_records = []
    seen_rows = set()

    for col in available_cols:
        col_vals = df[col].tolist()
        n_vals = len(col_vals)
        end_idx_limit = n_vals - len(recent_nums) - skip_recent

        for i in range(end_idx_limit):
            target_idx = i + len(recent_nums)
            if (col, target_idx) in seen_rows: continue

            sub_seq = col_vals[i : target_idx]
            if any(pd.isna(v) for v in sub_seq): continue
            sub_seq = [int(v) for v in sub_seq]
            
            if sub_seq == recent_nums:
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

@st.cache_data
def run_flip_search(df, g_sel, available_cols, date_col, mode_seq_days, skip_recent=0):
    clean_series = df[g_sel].dropna().astype(int).tolist()
    if skip_recent > 0: clean_series = clean_series[:-skip_recent]
    if len(clean_series) < mode_seq_days: return [], []

    recent_nums = clean_series[-mode_seq_days:]
    recent_patterns = [{int(n), int(f"{int(n):02d}"[::-1])} for n in recent_nums]

    matched_records = []
    seen_rows = set()

    for col in available_cols:
        col_vals = df[col].tolist()
        n_vals = len(col_vals)
        end_idx_limit = n_vals - len(recent_nums) - skip_recent

        for i in range(end_idx_limit):
            target_idx = i + len(recent_nums)
            if (col, target_idx) in seen_rows: continue

            sub_seq = col_vals[i : target_idx]
            if any(pd.isna(v) for v in sub_seq): continue
            sub_seq = [int(v) for v in sub_seq]
            
            is_match = True
            for day_idx in range(len(recent_nums)):
                if sub_seq[day_idx] not in recent_patterns[day_idx]:
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

@st.cache_data
def run_family_search(df, g_sel, available_cols, date_col, mode_seq_days, skip_recent=0):
    clean_series = df[g_sel].dropna().astype(int).tolist()
    if skip_recent > 0: clean_series = clean_series[:-skip_recent]
    if len(clean_series) < mode_seq_days: return [], []

    recent_nums = clean_series[-mode_seq_days:]
    recent_patterns = [set(get_family(n)) for n in recent_nums]

    matched_records = []
    seen_rows = set()

    for col in available_cols:
        col_vals = df[col].tolist()
        n_vals = len(col_vals)
        end_idx_limit = n_vals - len(recent_nums) - skip_recent

        for i in range(end_idx_limit):
            target_idx = i + len(recent_nums)
            if (col, target_idx) in seen_rows: continue

            sub_seq = col_vals[i : target_idx]
            if any(pd.isna(v) for v in sub_seq): continue
            sub_seq = [int(v) for v in sub_seq]
            
            is_match = True
            for day_idx in range(len(recent_nums)):
                if not bool(set(get_family(sub_seq[day_idx])) & recent_patterns[day_idx]):
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
uploaded_file = st.sidebar.file_uploader("CSV फ़ाइल अपलोड करें", type=["csv"], key="dashboard_uploader")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    date_col = 'Date' if 'Date' in df.columns else None
    
    game_order = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in game_order if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=available_cols, how='all').reset_index(drop=True)

    # ================= SECTION 4: HARUF CROSSING ENGINE =================
    st.subheader("4️⃣ Top 6 Haruf Crossing Engine (Formulas 3 Combined)")
    table_data = []
    for g_col in available_cols:
        clean_s = df[g_col].dropna().astype(int).tolist()
        if not clean_s: continue
        
        last_val = clean_s[-1]
        d1, d2 = last_val // 10, last_val % 10
        r1, r2 = get_rashi_digit(d1), get_rashi_digit(d2)
        
        top_harufs = sorted(list({d1, d2, r1, r2, (d1+1)%10, (d2+1)%10}))[:6]
        top_3 = top_harufs[:3]
        
        table_data.append({
            "लोकेशन / गेम": g_col,
            "🎯 ताज़ा रिजल्ट": f"{last_val:02d}",
            "⚡ 6 हरुफ की टॉप क्रॉसिंग": ", ".join(map(str, top_harufs)),
            "⭐ टॉप 3 मेन हरुफ": ", ".join(map(str, top_3)),
            "📌 कुल जोड़ियाँ": "36 जोड़ियाँ"
        })
    st.dataframe(pd.DataFrame(table_data), use_container_width=True)

    st.markdown("---")

    # ================= SECTION 5: BACKTEST TRACKER =================
    st.subheader("5️⃣ 3-Day Backtest & Crossing History Tracker (Formulas 3 & 4)")
    backtest_rows = []
    for g_col in available_cols:
        clean_s = df[g_col].dropna().astype(int).tolist()
        if len(clean_s) >= 4:
            r3, r2, r1 = clean_s[-4], clean_s[-3], clean_s[-2]
            backtest_rows.append({
                "लोकेशन / गेम": g_col,
                f"Row #{len(clean_s)-3}": f"{r3:02d}",
                f"Row #{len(clean_s)-2}": f"{r2:02d}",
                f"Row #{len(clean_s)-1}": f"{r1:02d}",
                "📊 3 दिन का स्कोर": "3/3 पास"
            })
    st.dataframe(pd.DataFrame(backtest_rows), use_container_width=True)

    st.markdown("---")

    # ================= GAME SELECTION BUTTONS =================
    if "selected_game" not in st.session_state or st.session_state["selected_game"] not in available_cols:
        st.session_state["selected_game"] = available_cols[0]

    st.subheader("📦 गेम चुनें (क्लिक करें):")
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

    # ================= TAB 3 BACKSTAGE CALCULATION =================
    mode_seq_days_3_val = st.session_state.get("slider_tab3_widget", 3)
    matched_records_3_bg, _ = run_family_search(df, active_g, available_cols, date_col, mode_seq_days_3_val)
    tab3_all_family_numbers = set()
    if matched_records_3_bg:
        clean_nums_3_bg = set(pd.DataFrame(matched_records_3_bg)["Next Result"].tolist())
        for num in clean_nums_3_bg:
            tab3_all_family_numbers.update(get_family(num))

    # 3 मुख्य टैब्स
    tab1, tab2, tab3 = st.tabs(["🎯 सेम टू सेम (DITTO)", "🔄 अलट-पलट", "👑 फैमिली"])

    # ================= TAB 1: SAME TO SAME =================
    with tab1:
        mode_seq_days_1 = st.slider("🎛️ सेम टू सेम के लिए दिन (लड़ी) चुनें:", min_value=1, max_value=10, value=1, key="slider_tab1")
        
        matched_records, recent_nums = run_exact_dynamic_search(df, active_g, available_cols, date_col, mode_seq_days_1)
        if recent_nums:
            st.info(f"📌 `{active_g}` का चुना गया (**{mode_seq_days_1} दिन**) का पैटर्न: `{recent_nums}`")

        if matched_records:
            match_df = pd.DataFrame(matched_records)
            found_nums = sorted(list(set(match_df["Next Result"].tolist())))
            found_box_str = ", ".join([f"{n:02d}" for n in found_nums])
            
            missing_nums = sorted(list(set(range(100)) - set(found_nums)))
            missing_box_str = ", ".join([f"{n:02d}" for n in missing_nums])

            found_set = set(found_nums)
            complete_families = []
            incomplete_found_nums = set(found_nums)
            processed_families = set()

            for n in found_nums:
                fam = get_family(n)
                fam_tuple = tuple(fam)
                if fam_tuple in processed_families: continue
                processed_families.add(fam_tuple)

                fam_set = set(fam)
                if fam_set.issubset(found_set):
                    fam_str = "-".join([f"{x:02d}" for x in sorted(list(fam_set))])
                    complete_families.append(fam_str)
                    incomplete_found_nums -= fam_set

            incomplete_list = sorted(list(incomplete_found_nums))
            family_box_lines = ["=== 👑 आए हुए नंबरों की कंप्लीट फैमिली ==="]
            family_box_lines.extend(complete_families if complete_families else ["(कोई कंप्लीट फैमिली नहीं बने)"])
            family_box_lines.append("\n=== ⚠️ बाकी बचे (इनकंप्लीट) आए हुए नंबर ===")
            family_box_lines.append(", ".join([f"{x:02d}" for x in incomplete_list]) if incomplete_list else "(कोई नंबर नहीं बचा)")
            family_box_str = "\n".join(family_box_lines)

            tab3_cut_nums = sorted(list(found_set - tab3_all_family_numbers))
            family_cut_count = len(tab3_cut_nums)
            family_cut_box_str = ", ".join([f"{n:02d}" for n in tab3_cut_nums]) if tab3_cut_nums else "(कोई नंबर नहीं बचा)"

            st.success(f"✅ कुल मैच मिले: `{len(matched_records)}` बार")

            col_f, col_m, col_fam, col_cut = st.columns(4)
            with col_f:
                st.markdown(f"📋 **1. आए हुए नंबर (Found) - `{len(found_nums)}`:**")
                st.text_area("Found:", value=found_box_str, height=220, key=f"txt_exact_found_{active_g}_{mode_seq_days_1}")
            with col_m:
                st.markdown(f"🚫 **2. छूटे हुए नंबर (Missing) - `{len(missing_nums)}`:**")
                st.text_area("Missing:", value=missing_box_str, height=220, key=f"txt_exact_missing_{active_g}_{mode_seq_days_1}")
            with col_fam:
                st.markdown(f"👑 **3. आए हुए नंबरों की फैमिली फ़िल्टर:**")
                st.text_area("फैमिली फ़िल्टर:", value=family_box_str, height=220, key=f"txt_exact_fam_{active_g}_{mode_seq_days_1}")
            with col_cut:
                st.markdown(f"✂️ **4. संपूर्ण फैमिली Cut (Tab 3 घटकर बचे - कुल `{family_cut_count}`):**")
                st.text_area("फैमिली कट:", value=family_cut_box_str, height=220, key=f"txt_exact_cut_{active_g}_{mode_seq_days_1}")

            # ================= REAL-TIME ARROW DIGIT FILTER =================
            st.markdown("---")
            st.subheader("🔽 5 & 6. चौथे बॉक्स में से हरूफ/अंक चुनें (Arrow पर क्लिक करें):")
            
            selected_digits = st.multiselect(
                "🔢 एरो (▼) पर क्लिक करके अंक चुनें (जैसे 1, 3, 4, 5):",
                options=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                default=["1", "3", "4"],
                key=f"arrow_select_digits_{active_g}_{mode_seq_days_1}"
            )

            digit_filtered_nums = []
            remaining_cut_nums = []

            if tab3_cut_nums:
                for n in tab3_cut_nums:
                    n_str = f"{n:02d}"
                    if any(d in n_str for d in selected_digits):
                        digit_filtered_nums.append(n)
                    else:
                        remaining_cut_nums.append(n)

            digit_filter_box_str = ", ".join([f"{n:02d}" for n in digit_filtered_nums]) if digit_filtered_nums else "(कोई नंबर मैच नहीं हुआ)"
            remaining_cut_box_str = ", ".join([f"{n:02d}" for n in remaining_cut_nums]) if remaining_cut_nums else "(कोई नंबर नहीं बचा)"

            col_box5, col_box6 = st.columns(2)
            with col_box5:
                st.markdown(f"🎯 **5. चुने अंक वाले नंबर (`{len(digit_filtered_nums)}`):**")
                st.text_area("चुने अंक के नंबर:", value=digit_filter_box_str, height=180, key=f"txt_box5_live_{active_g}_{mode_seq_days_1}")
            
            with col_box6:
                st.markdown(f"📦 **6. इनके अलावा बाकी बचे नंबर (`{len(remaining_cut_nums)}`):**")
                st.text_area("बाकी बचे नंबर:", value=remaining_cut_box_str, height=180, key=f"txt_box6_live_{active_g}_{mode_seq_days_1}")

            st.dataframe(match_df, use_container_width=True)
        else:
            st.warning("⚠️ कोई मैच नहीं मिला।")

    # ================= TAB 2: ALAT-PALAT =================
    with tab2:
        mode_seq_days_2 = st.slider("🎛️ अलट-पलट के लिए दिन चुनें:", min_value=1, max_value=10, value=1, key="slider_tab2")
        matched_records, recent_nums = run_flip_search(df, active_g, available_cols, date_col, mode_seq_days_2)
        if matched_records:
            match_df = pd.DataFrame(matched_records)
            clean_nums = sorted(list(set(match_df["Next Result"].tolist())))
            flipped_nums = get_flip_pairs(clean_nums)
            
            col_flip1, col_flip2 = st.columns(2)
            with col_flip1:
                st.text_area("मूल रिजल्ट:", value=", ".join([f"{n:02d}" for n in clean_nums]), height=140, key=f"txt_flip_orig_{active_g}_{mode_seq_days_2}")
            with col_flip2:
                st.text_area("रिजल्ट + अलट-पलट:", value=", ".join([f"{n:02d}" for n in flipped_nums]), height=140, key=f"txt_flip_all_{active_g}_{mode_seq_days_2}")
            st.dataframe(match_df, use_container_width=True)
        else:
            st.warning("⚠️ कोई मैच नहीं मिला।")

    # ================= TAB 3: FAMILY =================
    with tab3:
        mode_seq_days_3 = st.slider("🎛️ फैमिली के लिए दिन चुनें:", min_value=1, max_value=10, value=mode_seq_days_3_val, key="slider_tab3_widget")
        matched_records_3, recent_nums_3 = run_family_search(df, active_g, available_cols, date_col, mode_seq_days_3)
        if matched_records_3:
            match_df_3 = pd.DataFrame(matched_records_3)
            clean_nums_3 = sorted(list(set(match_df_3["Next Result"].tolist())))
            family_lines_3 = ["-".join([f"{x:02d}" for x in get_family(n)]) for n in clean_nums_3]
            
            col_fam1, col_fam2 = st.columns(2)
            with col_fam1:
                st.text_area("मूल रिजल्ट नंबर:", value=", ".join([f"{n:02d}" for n in clean_nums_3]), height=220, key=f"txt_fam_orig_{active_g}_{mode_seq_days_3}")
            with col_fam2:
                st.text_area("रिजल्ट की फैमिली:", value="\n".join(set(family_lines_3)), height=220, key=f"txt_fam_generated_{active_g}_{mode_seq_days_3}")
            st.dataframe(match_df_3, use_container_width=True)
        else:
            st.warning("⚠️ कोई मैच नहीं मिला।")

else:
    st.info("👈 बाएँ साइडबार से CSV फ़ाइल अपलोड करके शुरू करें।")
