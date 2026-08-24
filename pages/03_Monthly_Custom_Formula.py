import streamlit as st
import pandas as pd

st.set_page_config(page_title="1-Day Same-to-Same Detector", layout="wide")

st.title("🎯 1-डे सेम-टू-सेम (DITTO) डिटेक्टर डैशबोर्ड")

# ================= DYNAMIC FAST SEARCH ENGINE =================
@st.cache_data
def run_exact_dynamic_search(df, g_sel, available_cols, date_col, mode_seq_days, skip_recent=0):
    clean_series = df[g_sel].dropna().astype(int).tolist()
    if skip_recent > 0:
        clean_series = clean_series[:-skip_recent]
        
    if len(clean_series) < mode_seq_days:
        return [], []

    # जितने दिन का स्लाइडर चुना है, उतने ताज़ा रिज़ल्ट की लिस्ट बनेगी
    recent_nums = clean_series[-mode_seq_days:]

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
            
            # चुना हुआ sequence (1 या अधिक दिन) डिट्टो मैच हो रहा है या नहीं
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

    # 1. Slider: Default @ 1 Day
    mode_seq_days = st.slider("🎛️ दिन चुनें (डिफ़ॉल्ट 1 दिन):", min_value=1, max_value=10, value=1, key="ditto_slider")

    # 2. Search Function Call with Slider Value
    matched_records, recent_nums = run_exact_dynamic_search(df, active_g, available_cols, date_col, mode_seq_days)

    if recent_nums:
        nums_str = ", ".join([f"{n:02d}" for n in recent_nums])
        st.info(f"📌 **{active_g}** का चुना गया (**{mode_seq_days} दिन**) का पैटर्न: `{nums_str}`")

    if matched_records:
        match_df = pd.DataFrame(matched_records)
        
        # 1. आए हुए नंबर (Matched / Found Numbers)
        found_nums = sorted(list(set(match_df["Next Result"].tolist())))
        found_box_str = ", ".join([f"{n:02d}" for n in found_nums])
        
        # 2. छूटे हुए नंबर (Missing Numbers from 00-99)
        all_100_nums = set(range(100))
        missing_nums = sorted(list(all_100_nums - set(found_nums)))
        missing_box_str = ", ".join([f"{n:02d}" for n in missing_nums])

        st.success(f"✅ कुल मैच मिले: `{len(matched_records)}` बार")
        
        # Unique keys used for text_area so state updates seamlessly per game/slider change
        col_f, col_m = st.columns(2)
        
        with col_f:
            st.markdown(f"📋 **1. आए हुए नंबर (Matched / Found) - कुल `{len(found_nums)}`:**")
            st.text_area("कॉपी करें (Found Numbers):", value=found_box_str, height=150, key=f"txt_found_{active_g}_{mode_seq_days}")

        with col_m:
            st.markdown(f"🚫 **2. छूटे हुए नंबर (Missing Numbers) - कुल `{len(missing_nums)}`:**")
            st.text_area("कॉपी करें (Missing Numbers):", value=missing_box_str, height=150, key=f"txt_missing_{active_g}_{mode_seq_days}")

        st.subheader("📊 सभी मिलान का विस्तृत रिकॉर्ड:")
        st.dataframe(match_df, use_container_width=True)
    else:
        st.warning(f"⚠️ `{active_g}` के पैटर्न `{recent_nums}` के लिए कोई मैच नहीं मिला।")

else:
    st.info("👈 बाएँ साइडबार से CSV फ़ाइल अपलोड करके शुरू करें।")
    
        # ================= TAB 5: फैमिली (ORIGINAL + ALL FLIPPED FAMILIES) =================
        with sub_tab5:
            matched_records, recent_nums = run_fast_sequence_search(df, active_g, available_cols, date_col, mode_id="5", mode_seq_days=mode_seq_days)
            st.info(f"📌 `{active_g}` का पिछले **{mode_seq_days} दिन** का फैमिली पैटर्न: `{recent_nums}`")

            if matched_records:
                match_df = pd.DataFrame(matched_records)
                
                # 1. आए हुए मूल Next Result नंबर
                clean_nums = sorted(list(set(match_df["Next Result"].tolist())))
                box_str = ", ".join([f"{n:02d}" for n in clean_nums])
                
                # 2. आए हुए (Next Result) नंबरों की पूरी 8-8 जोड़ियों की फैमिली (अलट-पलट + राशि के साथ)
                matched_family_set = set()
                for num in clean_nums:
                    matched_family_set.update(get_family(num))  # इसमें पूरी अलट-पलट शामिल है
                
                matched_fam_nums = sorted(list(matched_family_set))
                matched_fam_box_str = ", ".join([f"{n:02d}" for n in matched_fam_nums])

                st.success(f"✅ मैच पाए गए: `{len(matched_records)}` बार")
                
                # दो अलग-अलग कॉपी-पेस्ट के डब्बे
                col_fam1, col_fam2 = st.columns(2)
                
                with col_fam1:
                    st.markdown(f"📋 **1. आए हुए Next Result (कुल `{len(clean_nums)}` नंबर):**")
                    st.text_area("कॉपी करें (Next Result):", value=box_str, height=140, key=f"copy_fam_{active_g}_{mode_seq_days}")

                with col_fam2:
                    st.markdown(f"👑 **2. आए हुए Next Result की पूरी फैमिली (राशि + अलट-पलट समेत कुल `{len(matched_fam_nums)}` जोड़ियाँ):**")
                    st.text_area("कॉपी करें (Next Result Family + अलट-पलट):", value=matched_fam_box_str, height=140, key=f"copy_matched_fam_{active_g}_{mode_seq_days}")

                st.dataframe(match_df, use_container_width=True)
            else:
                st.warning("⚠️ कोई मैच नहीं मिला।")
                
