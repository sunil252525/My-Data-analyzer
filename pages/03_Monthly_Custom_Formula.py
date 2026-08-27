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
    """आए हुए नंबरों और उनकी अलट-पलट को मिलाकर यूनिक (बिना डुप्लीकेट) लिस्ट बनाता है"""
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

    # स्लाइडर
    mode_seq_days = st.slider("🎛️ दिन (लड़ी) चुनें:", min_value=1, max_value=10, value=1, key="main_slider")

    # 3 मुख्य टैब्स
    tab1, tab2, tab3 = st.tabs(["🎯 सेम टू सेम (DITTO)", "🔄 अलट-पलट", "👑 फैमिली"])

    # ================= TAB 1: SAME TO SAME (DITTO) =================
    with tab1:
        matched_records, recent_nums = run_exact_dynamic_search(df, active_g, available_cols, date_col, mode_seq_days)
        if recent_nums:
            st.info(f"📌 `{active_g}` का चुना गया (**{mode_seq_days} दिन**) का पैटर्न: `{recent_nums}`")

        if matched_records:
            match_df = pd.DataFrame(matched_records)
            found_nums = sorted(list(set(match_df["Next Result"].tolist())))
            found_box_str = ", ".join([f"{n:02d}" for n in found_nums])
            
            missing_nums = sorted(list(set(range(100)) - set(found_nums)))
            missing_box_str = ", ".join([f"{n:02d}" for n in missing_nums])

            # --- शुद्ध आए हुए नंबरों के आधार पर फैमिली वर्गीकरण ---
            found_set = set(found_nums)
            complete_families = []
            incomplete_found_nums = set(found_nums) # शुरुआती तौर पर सभी आए हुए नंबर

            processed_families = set()

            for n in found_nums:
                fam = get_family(n)
                fam_tuple = tuple(fam)
                if fam_tuple in processed_families:
                    continue
                processed_families.add(fam_tuple)

                fam_set = set(fam)
                # केवल तभी कंप्लीट माना जाएगा जब पूरी फैमिली के सभी 8 नंबर आए हुए नंबरों (found_set) में मौजूद हों
                if fam_set.issubset(found_set):
                    fam_str = "-".join([f"{x:02d}" for x in sorted(list(fam_set))])
                    complete_families.append(fam_str)
                    # जो कंप्लीट हो गए, उन्हें इनकंप्लीट की लिस्ट से हटा देंगे
                    incomplete_found_nums -= fam_set

            incomplete_list = sorted(list(incomplete_found_nums))
            incomplete_str = ", ".join([f"{x:02d}" for x in incomplete_list])

            # तीसरे बॉक्स के लिए टेक्स्ट फॉर्मेट
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

            st.success(f"✅ कुल मैच मिले: `{len(matched_records)}` बार")

            # 3 Columns Layout
            col_f, col_m, col_fam = st.columns(3)
            with col_f:
                st.markdown(f"📋 **1. आए हुए नंबर (Found) - `{len(found_nums)}`:**")
                st.text_area("कॉपी करें (Found Numbers):", value=found_box_str, height=220, key=f"txt_exact_found_{active_g}_{mode_seq_days}")
            with col_m:
                st.markdown(f"🚫 **2. छूटे हुए नंबर (Missing) - `{len(missing_nums)}`:**")
                st.text_area("कॉपी करें (Missing Numbers):", value=missing_box_str, height=220, key=f"txt_exact_missing_{active_g}_{mode_seq_days}")
            with col_fam:
                st.markdown(f"👑 **3. आए हुए नंबरों की फैमिली फ़िल्टर:**")
                st.text_area("कॉपी करें (फैमिली विश्लेषण):", value=family_box_str, height=220, key=f"txt_exact_fam_{active_g}_{mode_seq_days}")

            st.dataframe(match_df, use_container_width=True)
        else:
            st.warning("⚠️ कोई मैच नहीं मिला।")

    # ================= TAB 2: ALAT-PALAT =================
    with tab2:
        matched_records, recent_nums = run_flip_search(df, active_g, available_cols, date_col, mode_seq_days)
        if recent_nums:
            st.info(f"📌 `{active_g}` का अलट-पलट (**{mode_seq_days} दिन**) पैटर्न: `{recent_nums}`")

        if matched_records:
            match_df = pd.DataFrame(matched_records)
            
            # 1. आए हुए मूल Next Result नंबर (Unique - डुप्लीकेट नहीं)
            clean_nums = sorted(list(set(match_df["Next Result"].tolist())))
            box_str = ", ".join([f"{n:02d}" for n in clean_nums])
            
            # 2. आए हुए सभी रिजल्ट नंबरों की अलट-पलट जोड़ियाँ (Unique - डुप्लीकेट नहीं)
            flipped_nums = get_flip_pairs(clean_nums)
            flipped_box_str = ", ".join([f"{n:02d}" for n in flipped_nums])
            
            st.success(f"✅ कुल मैच मिले: `{len(matched_records)}` बार")
            
            col_flip1, col_flip2 = st.columns(2)
            with col_flip1:
                st.markdown(f"📋 **1. आए हुए मूल Next Result (कुल `{len(clean_nums)}` नंबर):**")
                st.text_area("कॉपी करें (मूल रिजल्ट):", value=box_str, height=140, key=f"txt_flip_orig_{active_g}_{mode_seq_days}")

            with col_flip2:
                st.markdown(f"🔄 **2. आए हुए रिजल्ट + उनकी अलट-पलट (कुल `{len(flipped_nums)}` जोड़ियाँ):**")
                st.text_area("कॉपी करें (रिजल्ट + अलट-पलट):", value=flipped_box_str, height=140, key=f"txt_flip_all_{active_g}_{mode_seq_days}")

            st.dataframe(match_df, use_container_width=True)
        else:
            st.warning("⚠️ कोई मैच नहीं मिला।")

    # ================= TAB 3: FAMILY =================
    with tab3:
        matched_records, recent_nums = run_family_search(df, active_g, available_cols, date_col, mode_seq_days)
        if recent_nums:
            st.info(f"📌 `{active_g}` का फैमिली (**{mode_seq_days} दिन**) पैटर्न: `{recent_nums}`")

        if matched_records:
            match_df = pd.DataFrame(matched_records)
            
            # 1. आए हुए मूल Next Result नंबर
            clean_nums = sorted(list(set(match_df["Next Result"].tolist())))
            box_str = ", ".join([f"{n:02d}" for n in clean_nums])
            
            # 2. आए हुए Next Result नंबरों की पूरी अलट-पलट + राशि समेत फैमिली जोड़ियाँ
            matched_family_set = set()
            for num in clean_nums:
                matched_family_set.update(get_family(num))
            
            matched_fam_nums = sorted(list(matched_family_set))
            matched_fam_box_str = ", ".join([f"{n:02d}" for n in matched_fam_nums])

            st.success(f"✅ कुल मैच मिले: `{len(matched_records)}` बार")
            
            col_fam1, col_fam2 = st.columns(2)
            with col_fam1:
                st.markdown(f"📋 **1. आए हुए मूल Next Result (कुल `{len(clean_nums)}` नंबर):**")
                st.text_area("कॉपी करें (मूल रिजल्ट नंबर):", value=box_str, height=140, key=f"txt_fam_orig_{active_g}_{mode_seq_days}")

            with col_fam2:
                st.markdown(f"👑 **2. आए हुए रिजल्ट की संपूर्ण फैमिली (राशि + अलट-पलट समेत `{len(matched_fam_nums)}` जोड़ियाँ):**")
                st.text_area("कॉपी करें (रिजल्ट की पूरी फैमिली):", value=matched_fam_box_str, height=140, key=f"txt_fam_generated_{active_g}_{mode_seq_days}")

            st.dataframe(match_df, use_container_width=True)
        else:
            st.warning("⚠️ कोई मैच नहीं मिला।")

else:
    st.info("👈 बाएँ साइडबार से CSV फ़ाइल अपलोड करके शुरू करें।")
