import streamlit as st
import pandas as pd
import numpy as np

# ================= HELPER FUNCTIONS =================
RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi_digit(d):
    return RASHI_MAP.get(int(d), int(d))

def get_family(num):
    try:
        if pd.isna(num): return []
        num = int(num)
        d1, d2 = num // 10, num % 10
        r1, r2 = get_rashi_digit(d1), get_rashi_digit(d2)
        fam = set()
        for a, b in [(d1, d2), (d1, r2), (r1, d2), (r1, r2)]:
            fam.add(a * 10 + b)
            fam.add(b * 10 + a)
        return sorted(list(fam))
    except:
        return []

def show_new_formulas(df, available_cols, date_col=None):
    st.title("📊 Advance Analytics & Extra Formulas")

    # ================= FORMULA 1 =================
    st.subheader("1️⃣ Single Number Search Engine")
    search_num = st.number_input("नंबर चुनें (0-99):", min_value=0, max_value=99, value=88, step=1, key="f1_num")
    
    f1_results = []
    for col in available_cols:
        vals = df[col].dropna().astype(int).tolist()
        cnt = vals.count(search_num)
        f1_results.append({"लोकेशन / गेम": col, "कुल बार आया": cnt})
    st.dataframe(pd.DataFrame(f1_results), use_container_width=True)

    # ================= FORMULA 2 =================
    st.markdown("---")
    st.subheader("2️⃣ Family Search Engine")
    fam_input = st.text_input("फैमिली के नंबर डालें (कॉमा से अलग करें, उदा: 02, 07, 20, 25, 52, 57, 70, 75):", "02, 07, 20, 25, 52, 57, 70, 75", key="f2_fam")
    
    try:
        fam_nums = [int(x.strip()) for x in fam_input.split(",") if x.strip().isdigit()]
        f2_results = []
        for col in available_cols:
            vals = df[col].dropna().astype(int).tolist()
            cnt = sum(vals.count(n) for n in fam_nums)
            f2_results.append({"लोकेशन / गेम": col, "फैमिली पासिंग बार": cnt})
        st.dataframe(pd.DataFrame(f2_results), use_container_width=True)
    except Exception as e:
        st.error("कृपया सही फ़ॉर्मेट में नंबर दर्ज करें।")

    # ================= FORMULA 3 =================
    st.markdown("---")
    st.subheader("3️⃣ Location Hit Engine")
    f3_results = []
    for col in available_cols:
        cnt = df[col].dropna().count()
        f3_results.append({"लोकेशन / गेम": col, "कुल रिकॉर्ड्स": cnt})
    st.dataframe(pd.DataFrame(f3_results), use_container_width=True)

    # ================= FORMULA 4 =================
    st.markdown("---")
    st.subheader("4️⃣ Next 2 Days Follow-up Engine")
    trigger_num = st.number_input("ट्रिगर नंबर चुनें (जिसके बाद देखना है):", min_value=0, max_value=99, value=88, step=1, key="f4_trig")
    
    follow_list = []
    for col in available_cols:
        vals = df[col].dropna().astype(int).tolist()
        for i in range(len(vals) - 1):
            if vals[i] == trigger_num:
                if i + 1 < len(vals):
                    follow_list.append(vals[i + 1])
                if i + 2 < len(vals):
                    follow_list.append(vals[i + 2])
                    
    if follow_list:
        s_counts = pd.Series(follow_list).value_counts().head(5)
        st.write(f"🔥 **{trigger_num} के अगले 2 दिनों में सबसे ज़्यादा आने वाले नंबर:**")
        st.dataframe(pd.DataFrame({"नंबर": [f"{n:02d}" for n in s_counts.index], "कुल बार आया": s_counts.values}), use_container_width=True)
    else:
        st.info("इस नंबर का कोई फॉलो-अप डेटा नहीं मिला।")

    # ================= FORMULA 5 =================
    st.markdown("---")
    st.subheader("5️⃣ Top 5 Single Numbers (Location-wise)")
    f5_res = []
    for col in available_cols:
        vals = df[col].dropna().astype(int).tolist()
        if vals:
            top_5 = pd.Series(vals).value_counts().head(5).to_dict()
            f5_res.append({"लोकेशन / गेम": col, "टॉप 5 नंबर (बार)": str({f"{k:02d}": v for k, v in top_5.items()})})
    st.dataframe(pd.DataFrame(f5_res), use_container_width=True)

    # ================= FORMULA 6 =================
    st.markdown("---")
    st.subheader("6️⃣ Repeat Number Engine")
    f7_res = []
    for col in available_cols:
        vals = df[col].dropna().astype(int).tolist()
        rep_cnt = sum(1 for i in range(1, len(vals)) if vals[i] == vals[i-1])
        f7_res.append({"लोकेशन / गेम": col, "लगातार 2 दिन सेम नंबर (Repeat)": rep_cnt})
    st.dataframe(pd.DataFrame(f7_res), use_container_width=True)

    # ================= FORMULA 7 =================
    st.markdown("---")
    st.subheader("7️⃣ Odd/Even Ratio Engine")
    f8_res = []
    for col in available_cols:
        vals = df[col].dropna().astype(int).tolist()
        even_cnt = sum(1 for x in vals if x % 2 == 0)
        odd_cnt = len(vals) - even_cnt
        f8_res.append({"लोकेशन / गेम": col, "सम (Even)": even_cnt, "विषम (Odd)": odd_cnt})
    st.dataframe(pd.DataFrame(f8_res), use_container_width=True)

    # ================= FORMULA 8 =================
    st.markdown("---")
    st.subheader("8️⃣ Haruf Analysis Engine")
    f9_res = []
    for col in available_cols:
        vals = df[col].dropna().astype(int).tolist()
        inside = [x // 10 for x in vals]
        outside = [x % 10 for x in vals]
        top_in = pd.Series(inside).value_counts().idxmax() if inside else "-"
        top_out = pd.Series(outside).value_counts().idxmax() if outside else "-"
        f9_res.append({"लोकेशन / गेम": col, "अंदर का सबसे हॉट हरूफ़": top_in, "बाहर का सबसे हॉट हरूफ़": top_out})
    st.dataframe(pd.DataFrame(f9_res), use_container_width=True)

    # ================= FORMULA 9 =================
    st.markdown("---")
    st.subheader("9️⃣ Pair / Jodi Analysis Engine")
    f10_res = []
    for col in available_cols:
        vals = df[col].dropna().astype(int).tolist()
        jodi_cnt = sum(1 for x in vals if x // 10 == x % 10)
        f10_res.append({"लोकेशन / गेम": col, "जोड़ा (उदा: 11, 22, 88) कुल बार": jodi_cnt})
    st.dataframe(pd.DataFrame(f10_res), use_container_width=True)

    # ================= FORMULA 10 =================
    st.markdown("---")
    st.subheader("🔟 Family Scanner (Target & Rare Number)")

    c_target, c_days = st.columns(2)
    with c_target:
        scan_target = st.number_input("जिस रेयर/टारगेट नंबर का इतिहास चेक करना है (उदा. 20, 34, 88):", 0, 99, 88, key="scan_target_num_nf")
    with c_days:
        follow_days = st.radio("कितने दिनों के अंदर का ट्रैक रिकॉर्ड देखना है?", [1, 2], index=1, key="follow_days_radio_nf")

    if st.button("🔍 13 साल का इतिहास स्कैन करें", key="run_scan_10_nf"):
        hist_records = []
        direct_hits = []
        family_hits = []
        location_hits = []

        for col in available_cols:
            col_series = df[col].dropna().reset_index(drop=True)
            
            for idx in range(len(col_series) - follow_days):
                if int(col_series[idx]) == scan_target:
                    next_found_nums = []

                    for day_offset in range(1, follow_days + 1):
                        target_row_idx = idx + day_offset
                        if target_row_idx < len(df):
                            for g_col in available_cols:
                                val = df.loc[target_row_idx, g_col]
                                if pd.notna(val):
                                    val_int = int(val)
                                    next_found_nums.append(val_int)
                                    location_hits.append(g_col)
                                    fam_list = get_family(val_int)
                                    if fam_list:
                                        family_hits.append(f"फैमिली {fam_list[0]:02d}")

                    for n in next_found_nums:
                        direct_hits.append(n)

                    rec_date = df.loc[idx, 'Date'] if 'Date' in df.columns else f"Row #{idx}"
                    unique_next_nums = sorted(list(set(next_found_nums)))
                    
                    hist_records.append({
                        "तारीख़ / रो": rec_date,
                        "लोकेशन": col,
                        "टारगेट नंबर": f"{scan_target:02d}",
                        "अगले दिनों के यूनिक नंबर": str([f"{n:02d}" for n in unique_next_nums])
                    })

        if hist_records:
            st.success(f"🎯 **13 साल के रिकॉर्ड में नंबर {scan_target:02d} कुल {len(hist_records)} बार आया है!**")
            
            top_single = pd.Series(direct_hits).value_counts().head(1)
            top_fam = pd.Series(family_hits).value_counts().head(1)
            top_loc = pd.Series(location_hits).value_counts().head(1)

            s_num = f"{top_single.index[0]:02d}" if not top_single.empty else "N/A"
            s_cnt = top_single.values[0] if not top_single.empty else 0
            
            f_name = top_fam.index[0] if not top_fam.empty else "N/A"
            f_cnt = top_fam.values[0] if not top_fam.empty else 0
            
            l_name = top_loc.index[0] if not top_loc.empty else "N/A"
            l_cnt = top_loc.values[0] if not top_loc.empty else 0

            st.markdown(f"""
            🏆 **मुख्य निष्कर्ष (Summary):**
            * 💥 **सबसे ज़्यादा बार आने वाला सिंगल नंबर:** {s_num} (कुल {s_cnt} बार)
            * 👑 **सबसे ज़्यादा पास होने वाली फैमिली:** {f_name} (कुल {f_cnt} बार)
            * 📍 **सबसे ज़्यादा पासिंग देने वाली लोकेशन/गेम:** {l_name} (कुल {l_cnt} पासिंग)
            """)
            
            st.dataframe(pd.DataFrame(hist_records), use_container_width=True)
        else:
            st.warning("इतिहास में इस नंबर का कोई रिकॉर्ड नहीं मिला।")

    # ================= FORMULA 11 =================
    st.markdown("---")
    st.subheader("1️⃣1️⃣ Continuous 2-Month Pair Repeat Engine")

    detected_date_col = None
    for c in df.columns:
        if any(term in str(c).lower() for term in ['date', 'dt', 'tarikh', 'tariq', 'time', 'दिन', 'तारीख']):
            detected_date_col = c
            break

    if detected_date_col is None and date_col and date_col in df.columns:
        detected_date_col = date_col

    if detected_date_col:
        temp_df = df.copy()
        temp_df['dt'] = pd.to_datetime(temp_df[detected_date_col], dayfirst=True, errors='coerce')
        temp_df = temp_df.dropna(subset=['dt']).reset_index(drop=True)
        
        temp_df['Pair_Code'] = (temp_df['dt'].dt.month - 1) // 2
        temp_df['Pair_Year_ID'] = temp_df['dt'].dt.year.astype(str) + "_P" + temp_df['Pair_Code'].astype(str)
        
        pair_names = [
            "1. जनवरी - फ़रवरी (Jan-Feb)",
            "2. मार्च - अप्रैल (Mar-Apr)",
            "3. मई - जून (May-Jun)",
            "4. जुलाई - अगस्त (Jul-Aug)",
            "5. सितंबर - अक्टूबर (Sep-Oct)",
            "6. नवंबर - दिसंबर (Nov-Dec)"
        ]

        tab1, tab2 = st.tabs(["🔄 लगातार 2-महीने के जोड़ों में आने वाले सदाबहार नंबर", "📆 2-महीने के पेयर (जैसे Jan-Feb) के अनुसार रिज़ल्ट"])

        with tab1:
            all_pair_blocks = sorted(temp_df['Pair_Year_ID'].unique())
            total_blocks_count = len(all_pair_blocks)
            pair_consistency_res = []
            
            for col in available_cols:
                num_block_map = {n: set() for n in range(100)}
                num_total_count = {n: 0 for n in range(100)}
                
                for idx, row in temp_df.iterrows():
                    val = row[col]
                    if pd.notna(val):
                        try:
                            n = int(val)
                            if 0 <= n <= 99:
                                num_block_map[n].add(row['Pair_Year_ID'])
                                num_total_count[n] += 1
                        except:
                            continue
                
                sorted_nums = sorted(num_block_map.keys(), key=lambda x: len(num_block_map[x]), reverse=True)
                
                top_1 = sorted_nums[0]
                top_1_b = len(num_block_map[top_1])
                top_1_tot = num_total_count[top_1]
                top_1_rate = round((top_1_b / total_blocks_count) * 100, 1) if total_blocks_count > 0 else 0
                top_2 = sorted_nums[1]
                top_2_b = len(num_block_map[top_2])
                
                pair_consistency_res.append({
                    "लोकेशन / गेम": col,
                    "👑 #1 सबसे ज़्यादा रिपीट नंबर": f"{top_1:02d}",
                    "कितने 2-महीने के जोड़ों में आया": f"{top_1_b} / {total_blocks_count} पेयर्स ({top_1_rate}%)",
                    "कुल बार गिरा": f"{top_1_tot} बार",
                    "🥈 #2 दूसरा बेस्ट नंबर": f"{top_2:02d} ({top_2_b} पेयर्स में)",
                })
            
            st.dataframe(pd.DataFrame(pair_consistency_res), use_container_width=True)

        with tab2:
            selected_pair_idx = st.selectbox("2 महीने का जोड़ा चुनें:", range(6), format_func=lambda x: pair_names[x], key="f11_pair_select_nf")
            
            p_filtered = temp_df[temp_df['Pair_Code'] == selected_pair_idx]
            p_results = []
            
            for col in available_cols:
                vals = p_filtered[col].dropna().astype(int).tolist()
                if vals:
                    counts = pd.Series(vals).value_counts()
                    top_n = counts.index[0]
                    top_cnt = counts.iloc[0]
                    top_5_dict = counts.head(5).to_dict()
                    
                    p_results.append({
                        "लोकेशन / गेम": col,
                        "🔥 सबसे हॉट नंबर": f"{top_n:02d}",
                        "कितनी बार आया": f"{top_cnt} बार",
                        "टॉप 5 नंबर (बार)": str({f"{k:02d}": v for k, v in top_5_dict.items()})
                    })
            
            st.dataframe(pd.DataFrame(p_results), use_container_width=True)

    else:
        st.error("⚠️ तारीख़ का कॉलम (Date) नहीं मिला।")
