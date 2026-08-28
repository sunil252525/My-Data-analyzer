import streamlit as st
import pandas as pd

st.set_page_config(page_title="Same-to-Same & Family Detector", layout="wide")

st.title("🎯 सेम-टू-सेम, अलट-पलट & फैमिली डिटेक्टर डैशबोर्ड")

# ================= HELPER FUNCTIONS =================
RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi_digit(d):
    try: return RASHI_MAP.get(int(d), int(d))
    except: return 0

def get_family(num):
    """राशि + अलट-पलट के साथ 8 जोड़ियों की फैमिली जनरेट करता है"""
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
    """आए हुए नंबरों और उनकी अलट-पलट को मिलाकर यूनिक लिस्ट बनाता है"""
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
    if skip_recent > 0:
        clean_series = clean_series[:-skip_recent]
        
    if len(clean_series) < mode_seq_days:
        return [], []

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
    st.markdown("---")

    # 3 मुख्य टैब्स
    tab1, tab2, tab3 = st.tabs(["🎯 सेम टू सेम (DITTO)", "🔄 अलट-पलट", "👑 फैमिली"])

    if "slider_tab3" not in st.session_state:
        st.session_state["slider_tab3"] = 3

    # 🔥 Fix: बैकग्राउंड में Tab 3 की फैमिली पहले निकालें ताकि 4th, 5th, 6th बॉक्स सही रहें
    tab3_all_family_numbers = set()
    mode_seq_days_3 = st.session_state.get("slider_tab3", 3)
    matched_records_3, recent_nums_3 = run_family_search(df, active_g, available_cols, date_col, mode_seq_days_3)
    
    if matched_records_3:
        clean_nums_3_bg = set(pd.DataFrame(matched_records_3)["Next Result"].tolist())
        for num in clean_nums_3_bg:
            tab3_all_family_numbers.update(get_family(num))

    # ================= TAB 1: SAME TO SAME (DITTO) =================
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

            # --- 3. आए हुए नंबरों की फैमिली फ़िल्टर ---
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
            incomplete_str = ", ".join([f"{x:02d}" for x in incomplete_list])

            family_box_lines = []
            family_box_lines.append("=== 👑 आए हुए नंबरों की कंप्लीट फैमिली ===")
            if complete_families:
                family_box_lines.extend(complete_families)
            else:
                family_box_lines.append("(कोई कंप्लीट फैमिली नहीं बनी)")

            family_box_lines.append("\n=== ⚠️ बाकी बचे (इनकंप्लीट) आए हुए नंबर ===")
            if incomplete_list:
                family_box_lines.append(incomplete_str)
            else:
                family_box_lines.append("(कोई नंबर नहीं बचा)")

            family_box_str = "\n".join(family_box_lines)

            # --- 4. चौथे बॉक्स के लिए (Tab 1 के Found Numbers - Tab 3 की सम्पूर्ण फैमिली) ---
            tab3_cut_nums = sorted(list(found_set - tab3_all_family_numbers))
            family_cut_count = len(tab3_cut_nums)
            family_cut_box_str = ", ".join([f"{n:02d}" for n in tab3_cut_nums]) if tab3_cut_nums else "(कोई नंबर नहीं बचा)"

            st.success(f"✅ कुल मैच मिले: `{len(matched_records)}` बार")

            col_f, col_m, col_fam, col_cut = st.columns(4)
            with col_f:
                st.markdown(f"📋 **1. आए हुए नंबर (Found) - `{len(found_nums)}`:**")
                st.text_area("कॉपी करें (Found Numbers):", value=found_box_str, height=220, key=f"txt_exact_found_{active_g}_{mode_seq_days_1}")
            with col_m:
                st.markdown(f"🚫 **2. छूटे हुए नंबर (Missing) - `{len(missing_nums)}`:**")
                st.text_area("कॉपी करें (Missing Numbers):", value=missing_box_str, height=220, key=f"txt_exact_missing_{active_g}_{mode_seq_days_1}")
            with col_fam:
                st.markdown(f"👑 **3. आए हुए नंबरों की फैमिली फ़िल्टर:**")
                st.text_area("कॉपी करें (फैमिली विश्लेषण):", value=family_box_str, height=220, key=f"txt_exact_fam_{active_g}_{mode_seq_days_1}")
            with col_cut:
                st.markdown(f"✂️ **4. संपूर्ण फैमिली Cut (Tab 3 घटकर बचे - कुल `{family_cut_count}` नंबर):**")
                st.text_area("कॉपी करें (फैमिली कट नंबर):", value=family_cut_box_str, height=220, key=f"txt_exact_cut_{active_g}_{mode_seq_days_1}")

            # ================= 5th & 6th BOX SECTION =================
            st.markdown("---")
            st.subheader("✏️ 5 & 6. चौथे बॉक्स में से अंक (डिजिट) फ़िल्टर:")
            
            user_digits_input = st.text_input(
                "🔢 चौथे बॉक्स के नंबरों में से जिन अंकों (जैसे 4 5 6) को अलग करना है, यहाँ लिखें:",
                value="4 5 6",
                key=f"digit_input_{active_g}_{mode_seq_days_1}"
            )

            # अंकों को सही से पढ़ना
            entered_digits = set(c for c in user_digits_input if c.isdigit())

            if tab3_cut_nums and entered_digits:
                # 5th Box: जिनमें चुने अंक मौजूद हैं
                digit_filtered_nums = [
                    n for n in tab3_cut_nums 
                    if any(ch in entered_digits for ch in f"{n:02d}")
                ]
                # 6th Box: जिनमें चुने अंक मौजूद नहीं हैं
                remaining_cut_nums = [
                    n for n in tab3_cut_nums 
                    if not any(ch in entered_digits for ch in f"{n:02d}")
                ]
            else:
                digit_filtered_nums = []
                remaining_cut_nums = tab3_cut_nums if tab3_cut_nums else []

            digit_filter_count = len(digit_filtered_nums)
            digit_filter_box_str = ", ".join([f"{n:02d}" for n in digit_filtered_nums]) if digit_filtered_nums else "(कोई नंबर मैच नहीं हुआ)"

            remaining_cut_count = len(remaining_cut_nums)
            remaining_cut_box_str = ", ".join([f"{n:02d}" for n in remaining_cut_nums]) if remaining_cut_nums else "(कोई नंबर नहीं बचा)"

            digits_display = ", ".join(sorted(list(entered_digits))) if entered_digits else "कोई नहीं"

            # 5th और 6th बॉक्स
            col_box5, col_box6 = st.columns(2)
            with col_box5:
                st.markdown(f"🎯 **5. चुने अंक वाले नंबर (अंक: `{digits_display}` - कुल `{digit_filter_count}` नंबर):**")
                st.text_area("कॉपी करें (चुने अंक के नंबर):", value=digit_filter_box_str, height=180, key=f"txt_exact_digit_filter_{active_g}_{mode_seq_days_1}")
            
            with col_box6:
                st.markdown(f"📦 **6. इनके अलावा बाकी बचे नंबर (कुल `{remaining_cut_count}` नंबर):**")
                st.text_area("कॉपी करें (बाकी बचे नंबर):", value=remaining_cut_box_str, height=180, key=f"txt_exact_remaining_cut_{active_g}_{mode_seq_days_1}")

            st.dataframe(match_df, use_container_width=True)
        else:
            st.warning("⚠️ कोई मैच नहीं मिला।")

    # ================= TAB 2: ALAT-PALAT =================
    with tab2:
        mode_seq_days_2 = st.slider("🎛️ अलट-पलट के लिए दिन (लड़ी) चुनें:", min_value=1, max_value=10, value=1, key="slider_tab2")
        
        matched_records, recent_nums = run_flip_search(df, active_g, available_cols, date_col, mode_seq_days_2)
        if recent_nums:
            st.info(f"📌 `{active_g}` का अलट-पलट (**{mode_seq_days_2} दिन**) पैटर्न: `{recent_nums}`")

        if matched_records:
            match_df = pd.DataFrame(matched_records)
            clean_nums = sorted(list(set(match_df["Next Result"].tolist())))
            box_str = ", ".join([f"{n:02d}" for n in clean_nums])
            
            flipped_nums = get_flip_pairs(clean_nums)
            flipped_box_str = ", ".join([f"{n:02d}" for n in flipped_nums])
            
            st.success(f"✅ कुल मैच मिले: `{len(matched_records)}` बार")
            
            col_flip1, col_flip2 = st.columns(2)
            with col_flip1:
                st.markdown(f"📋 **1. आए हुए मूल Next Result (कुल `{len(clean_nums)}` नंबर):**")
                st.text_area("कॉपी करें (मूल रिजल्ट):", value=box_str, height=140, key=f"txt_flip_orig_{active_g}_{mode_seq_days_2}")

            with col_flip2:
                st.markdown(f"🔄 **2. आए हुए रिजल्ट + उनकी अलट-पलट (कुल `{len(flipped_nums)}` जोड़ियाँ):**")
                st.text_area("कॉपी करें (रिजल्ट + अलट-पलट):", value=flipped_box_str, height=140, key=f"txt_flip_all_{active_g}_{mode_seq_days_2}")

            st.dataframe(match_df, use_container_width=True)
        else:
            st.warning("⚠️ कोई मैच नहीं मिला।")

    # ================= TAB 3: FAMILY =================
    with tab3:
        mode_seq_days_3 = st.slider("🎛️ फैमिली के लिए दिन (लड़ी) चुनें:", min_value=1, max_value=10, value=st.session_state.get("slider_tab3", 3), key="slider_tab3_widget")
        st.session_state["slider_tab3"] = mode_seq_days_3

        clean_nums_3 = []

        if matched_records_3:
            match_df_3 = pd.DataFrame(matched_records_3)
            clean_nums_3 = sorted(list(set(match_df_3["Next Result"].tolist())))
            box_str_3 = ", ".join([f"{n:02d}" for n in clean_nums_3])
            
            family_lines_3 = []
            processed_fam_tuples_3 = set()
            
            for num in clean_nums_3:
                fam = get_family(num)
                fam_tuple = tuple(fam)
                if fam_tuple not in processed_fam_tuples_3:
                    processed_fam_tuples_3.add(fam_tuple)
                    fam_line = "-".join([f"{x:02d}" for x in fam])
                    family_lines_3.append(fam_line)
            
            matched_fam_box_str_3 = "\n".join(family_lines_3)

            st.info(f"📌 `{active_g}` का फैमिली (**{mode_seq_days_3} दिन**) पैटर्न: `{recent_nums_3}`")
            st.success(f"✅ कुल मैच मिले: `{len(matched_records_3)}` बार")
            
            col_fam1, col_fam2 = st.columns(2)
            with col_fam1:
                st.markdown(f"📋 **1. आए हुए मूल Next Result (कुल `{len(clean_nums_3)}` नंबर):**")
                st.text_area("कॉपी करें (मूल रिजल्ट नंबर):", value=box_str_3, height=220, key=f"txt_fam_orig_{active_g}_{mode_seq_days_3}")

            with col_fam2:
                st.markdown(f"👑 **2. आए हुए रिजल्ट की संपूर्ण फैमिली (लाइन अनुसार):**")
                st.text_area("कॉपी करें (रिजल्ट की फैमिली लाइन बाई लाइन):", value=matched_fam_box_str_3, height=220, key=f"txt_fam_generated_{active_g}_{mode_seq_days_3}")

            st.dataframe(match_df_3, use_container_width=True)
        else:
            st.warning("⚠️ कोई मैच नहीं मिला।")

else:
    st.info("👈 बाएँ साइडबार से CSV फ़ाइल अपलोड करके शुरू करें।")
