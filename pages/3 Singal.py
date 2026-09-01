import streamlit as st
import pandas as pd
from collections import Counter
from itertools import combinations

st.set_page_config(page_title="Ultimate 13-Year Pattern & Target Detector", layout="wide")

st.title("🎯 Ultimate 13-Year Master Pattern & Target Detector v5.0")

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

def get_family_head(num):
    fam = get_family(num)
    return fam[0] if fam else num

def extract_haruf(num):
    try:
        n = int(num)
        return (n // 10, n % 10)
    except:
        return (None, None)

def get_sum_digit(num):
    try:
        n = int(num)
        return (n // 10) + (n % 10)
    except: return None

def get_odd_even_type(num):
    try:
        n = int(num)
        d1, d2 = n // 10, n % 10
        if d1 % 2 == 0 and d2 % 2 == 0: return "Even-Even (सम-सम)"
        elif d1 % 2 != 0 and d2 % 2 != 0: return "Odd-Odd (विषम-विषम)"
        else: return "Odd-Even (मिश्रित)"
    except: return "N/A"

# ================= SEARCH ENGINES =================
def analyze_target_occurrences(df, target_game, target_num, window_days=2):
    next_day_results = []
    window_results = []
    occurrences_log = []

    date_col = 'Date' if 'Date' in df.columns else None
    valid_df = df[[target_game] + ([date_col] if date_col else [])].dropna(subset=[target_game]).reset_index(drop=True)
    total_rows = len(valid_df)

    for idx in range(total_rows):
        val = valid_df.loc[idx, target_game]
        if pd.notna(val) and int(val) == target_num:
            rec_date = valid_df.loc[idx, date_col] if date_col else f"Row #{idx}"
            
            next_1_val = None
            if idx + 1 < total_rows and pd.notna(valid_df.loc[idx + 1, target_game]):
                next_1_val = int(valid_df.loc[idx + 1, target_game])
                next_day_results.append(next_1_val)

            win_vals = []
            for d in range(1, window_days + 1):
                if idx + d < total_rows and pd.notna(valid_df.loc[idx + d, target_game]):
                    v = int(valid_df.loc[idx + d, target_game])
                    win_vals.append(v)
                    window_results.append(v)

            occurrences_log.append({
                "तारीख / रो": rec_date,
                "गेम": target_game,
                "टारगेट नंबर": f"{target_num:02d}",
                "अगला दिन (+1 Day)": f"{next_1_val:02d}" if next_1_val is not None else "N/A",
                "2 दिन के अंदर": ", ".join([f"{v:02d}" for v in win_vals])
            })

    return occurrences_log, next_day_results, window_results


def find_similar_pattern_months(df, selected_game, last_days=5):
    date_col = 'Date' if 'Date' in df.columns else None
    valid_df = df[[selected_game] + ([date_col] if date_col else [])].dropna(subset=[selected_game]).reset_index(drop=True)
    clean_series = valid_df[selected_game].astype(int).tolist()
    
    if len(clean_series) < last_days + 3:
        return [], {}

    current_pattern = clean_series[-last_days:]
    ander_haruf = [extract_haruf(n)[0] for n in current_pattern if extract_haruf(n)[0] is not None]
    bahar_haruf = [extract_haruf(n)[1] for n in current_pattern if extract_haruf(n)[1] is not None]
    
    top_ander = Counter(ander_haruf).most_common(1)[0][0] if ander_haruf else "N/A"
    top_bahar = Counter(bahar_haruf).most_common(1)[0][0] if bahar_haruf else "N/A"

    matched_predictions = []

    for i in range(len(clean_series) - last_days - 3):
        sub_seq = clean_series[i : i + last_days]
        match_score = 0
        for idx in range(last_days):
            if sub_seq[idx] == current_pattern[idx]: match_score += 2
            elif set(get_family(sub_seq[idx])) & set(get_family(current_pattern[idx])): match_score += 1

        if match_score >= (last_days * 0.7):
            next_3_days = clean_series[i + last_days : i + last_days + 3]
            rec_date = valid_df.loc[i + last_days, date_col] if date_col else f"Row #{i+last_days}"
            matched_predictions.append({
                "ऐतिहासिक तारीख / रो": rec_date,
                "मैच हुआ पैटर्न": ", ".join([f"{n:02d}" for n in sub_seq]),
                "अगले 3 दिन के परिणाम": ", ".join([f"{n:02d}" for n in next_3_days])
            })

    pattern_info = {
        "वर्तमान चाल": ", ".join([f"{n:02d}" for n in current_pattern]),
        "सबसे ज़्यादा चलने वाला अंदर हर्फ़": top_ander,
        "सबसे ज़्यादा चलने वाला बाहर हर्फ़": top_bahar
    }

    return matched_predictions, pattern_info

# ================= SIDEBAR & FILE UPLOAD =================
st.sidebar.title("📌 फ़ाइल अपलोड & सेटिंग्स")
uploaded_file = st.sidebar.file_uploader("13 साल की CSV फ़ाइल अपलोड करें", type=["csv"], key="master_uploader")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    date_col = 'Date' if 'Date' in df.columns else None
    
    game_order = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in game_order if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    # मुख्य 7 टैब्स
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🎯 1. टारगेट सर्च", 
        "🔄 2. चाल & हर्फ़ पैटर्न", 
        "🔴 3. हॉट & कोल्ड हीटमैप", 
        "👑 4. ऑटो-पैटर्न चेज़र",
        "⚖️ 5. जोड़ & Odd/Even एनालिसिस",
        "💯 6. 00-99 & Haruf 100% Analysis",
        "🎯 7. Best 4-Digit Crossing (Next Day)"
    ])

    # ================= TAB 1: TARGET REPEAT =================
    with tab1:
        st.subheader("⚙️ टारगेट सर्च सेटिंग्स:")
        col_sel1, col_sel2, col_sel3 = st.columns(3)
        with col_sel1:
            selected_game = st.selectbox("🎯 गेम चुनें:", available_cols, index=available_cols.index('GALI') if 'GALI' in available_cols else 0, key="t1_game")
        with col_sel2:
            target_number = st.number_input("🔢 टारगेट नंबर दर्ज करें:", min_value=0, max_value=99, value=25, step=1, key="t1_num")
        with col_sel3:
            window_days = st.slider("📅 विंडो (कितने दिन के अंदर):", min_value=1, max_value=5, value=2, key="t1_win")

        st.markdown("---")
        logs, next_day_list, window_list = analyze_target_occurrences(df, selected_game, target_number, window_days)

        if logs:
            st.success(f"📊 **13 साल के डेटा में `{selected_game}` में `{target_number:02d}` कुल `{len(logs)}` बार आया है।**")
            
            single_counts = Counter(window_list)
            top_3_tuples = single_counts.most_common(3)
            top_3_singles = [item[0] for item in top_3_tuples]
            top_3_singles_str = ", ".join([f"{n:02d}" for n in top_3_singles])

            family_counts = Counter([get_family_head(num) for num in window_list])
            top_family_tuples = family_counts.most_common(3)
            top_families_heads = [item[0] for item in top_family_tuples]
            
            all_top_family_pairs = set()
            for f_head in top_families_heads:
                all_top_family_pairs.update(get_family(f_head))
            top_family_pairs_str = ", ".join([f"{n:02d}" for n in sorted(list(all_top_family_pairs))])

            col_box1, col_box2 = st.columns(2)
            with col_box1:
                st.markdown(f"🔥 **Top 3 रिपीट सिंगल नंबर:**")
                st.text_area("कॉपी करें (Single Repeat Numbers):", value=top_3_singles_str, height=100, key=f"txt_single_{selected_game}_{target_number}_{window_days}")
                for num, count in top_3_tuples: st.write(f"- नंबर **`{num:02d}`**: कुल **{count}** बार आया")

            with col_box2:
                st.markdown(f"👑 **Top 3 रिपीट फैमिलियों की संपूर्ण जोड़ियाँ:**")
                st.text_area("कॉपी करें (Top Repeat Family Numbers):", value=top_family_pairs_str, height=100, key=f"txt_family_{selected_game}_{target_number}_{window_days}")
                for f_head, count in top_family_tuples: st.write(f"- **`{f_head:02d}`** की फैमिली: कुल **{count}** बार पास हुई")

            st.markdown("---")
            st.subheader("📜 पूरा ऐतिहासिक रिकॉर्ड:")
            st.dataframe(pd.DataFrame(logs), use_container_width=True)
        else:
            st.warning("⚠️ चुना गया नंबर रिकॉर्ड में नहीं मिला।")

    # ================= TAB 2: MONTHLY PATTERN & HARUF =================
    with tab2:
        st.subheader("🔍 सेम पैटर्न & चाल मैचिंग सिस्टम")
        col_p1, col_p2 = st.columns(2)
        with col_p1: pat_game = st.selectbox("🎯 गेम चुनें:", available_cols, key="pat_game")
        with col_p2: last_days_scan = st.slider("📅 हाल के कितने दिनों का पैटर्न मैच करना है:", min_value=3, max_value=10, value=5, key="pat_days")

        matched_preds, info = find_similar_pattern_months(df, pat_game, last_days_scan)

        if info:
            st.info(f"📌 **`{pat_game}` का चालू पैटर्न ({last_days_scan} दिन):** `{info['वर्तमान चाल']}`")
            c_h1, c_h2 = st.columns(2)
            with c_h1: st.success(f"🔑 **चाल का मुख्य अंदर हर्फ़ (Ander):** `{info['सबसे ज़्यादा चलने वाला अंदर हर्फ़']}`")
            with c_h2: st.success(f"🔑 **चाल का मुख्य बाहर हर्फ़ (Bahar):** `{info['सबसे ज़्यादा चलने वाला बाहर हर्फ़']}`")

            st.markdown("---")
            if matched_preds:
                st.subheader(f"📜 मिले सेम पैटर्न वाले महीने (कुल `{len(matched_preds)}` बार):")
                st.dataframe(pd.DataFrame(matched_preds), use_container_width=True)
                
                all_next_res = []
                for row in matched_preds:
                    res_list = [int(x.strip()) for x in row["अगले 3 दिन के परिणाम"].split(",") if x.strip().isdigit()]
                    all_next_res.extend(res_list)
                
                top_next_3 = Counter(all_next_res).most_common(3)
                top_next_str = ", ".join([f"{n:02d}" for n, c in top_next_3])
                
                st.markdown("🔥 **सेम चाल के बाद सबसे ज्यादा खुलने वाले Top 3 परिणाम:**")
                st.text_area("कॉपी करें (Pattern Based Suggestions):", value=top_next_str, height=90, key="txt_pat_suggest")
            else:
                st.warning("⚠️ 70%+ मैच खाता हुआ रिकॉर्ड नहीं मिला।")

    # ================= TAB 3: HOT & COLD HEATMAP =================
    with tab3:
        st.subheader("🔴🔵 100 नंबरों का फ्रीक्वेंसी हीटमैप (Hot & Cold Chart)")
        heat_game = st.selectbox("🎯 गेम चुनें:", available_cols, key="heat_game")
        recent_scan_days = st.slider("📅 कितने हालिया दिनों में देखना है:", min_value=10, max_value=365, value=60, key="heat_days")
        
        valid_series = df[heat_game].dropna().reset_index(drop=True).tail(recent_scan_days).astype(int).tolist()
        num_counts = Counter(valid_series)
        
        hot_nums = [f"{n:02d}" for n, c in num_counts.most_common(10)]
        cold_nums = [f"{n:02d}" for n in range(100) if n not in num_counts]

        c_h1, c_h2 = st.columns(2)
        with c_h1:
            st.error(f"🔥 **Top 10 Hot Numbers (पिछले {recent_scan_days} दिनों में सबसे ज्यादा आए):**")
            st.text_area("कॉपी करें (Hot Numbers):", value=", ".join(hot_nums), height=100, key=f"txt_hot_{recent_scan_days}")
        with c_h2:
            st.info(f"❄️ **Cold Numbers (जो पिछले {recent_scan_days} दिनों से बिल्कुल नहीं आए):**")
            st.text_area("कॉपी करें (Cold Numbers):", value=", ".join(cold_nums), height=100, key=f"txt_cold_{recent_scan_days}")

        st.markdown("---")
        st.write("📊 **00 से 99 तक सभी 100 नंबरों की फ्रीक्वेंसी (कितनी बार आए):**")
        grid_cols = st.columns(10)
        for i in range(100):
            cnt = num_counts.get(i, 0)
            col_idx = i % 10
            with grid_cols[col_idx]:
                if cnt >= 3: st.markdown(f"🔴 **`{i:02d}`** ({cnt})")
                elif cnt == 0: st.markdown(f"🔵 `{i:02d}` (0)")
                else: st.markdown(f"🟡 `{i:02d}` ({cnt})")

    # ================= TAB 4: AUTO PATTERN HUNTER =================
    with tab4:
        st.subheader("👑 ऑटो-पैटर्न चेज़र (Automatic Trend Hunter)")
        st.info("यह सिस्टम डेटा को खुद स्कैन करके ट्रेंडिंग फैमिलियों और रिपीट जोड़ियों को ऑटो-डिटेक्ट करता है।")
        
        hunter_game = st.selectbox("🎯 गेम चुनें:", available_cols, key="hunt_game")
        hunt_days = st.slider("📅 हालिया दिनों की ट्रेंडिंग स्कैन करें:", min_value=5, max_value=30, value=15, key="hunt_days")

        recent_vals = df[hunter_game].dropna().tail(hunt_days).astype(int).tolist()
        if recent_vals:
            fam_heads = [get_family_head(n) for n in recent_vals]
            top_fam = Counter(fam_heads).most_common(2)
            
            st.success(f"⚡ **पिछले {hunt_days} दिनों में सबसे ज्यादा एक्टिव फैमिलियाँ:**")
            for f_h, count in top_fam:
                fam_members = get_family(f_h)
                fam_str = ", ".join([f"{x:02d}" for x in fam_members])
                st.markdown(f"👑 **`{f_h:02d}` की फैमिली (कुल {count} बार एक्टिव):** `{fam_str}`")

    # ================= TAB 5: SUM & ODD/EVEN ANALYSIS =================
    with tab5:
        st.subheader("⚖️ जोड़ (Sum) और Odd/Even का गहराई से विश्लेषण")
        sum_game = st.selectbox("🎯 गेम चुनें:", available_cols, key="sum_game")
        recent_sum_days = st.slider("📅 स्कैन करने के लिए हालिया दिन चुनें:", min_value=10, max_value=100, value=30, key="sum_days")

        sum_series = df[sum_game].dropna().tail(recent_sum_days).astype(int).tolist()
        
        sums = [get_sum_digit(n) for n in sum_series if get_sum_digit(n) is not None]
        sum_counts = Counter(sums)
        top_sums = sum_counts.most_common(3)
        top_sums_str = ", ".join([str(s) for s, c in top_sums])

        types = [get_odd_even_type(n) for n in sum_series]
        type_counts = Counter(types)

        c_s1, c_s2 = st.columns(2)
        with c_s1:
            st.success(f"🔢 **सबसे ज्यादा रिपीट होने वाले Top 3 अंकों के जोड़ (Sum):** `{top_sums_str}`")
            for s, c in top_sums: st.write(f"- जोड़ **`{s}`**: कुल **{c}** बार आया")
        
        with c_s2:
            st.info(f"⚖️ **Odd/Even कॉम्बिनेशन पैटर्न:**")
            for t, c in type_counts.items(): st.write(f"- **{t}**: **{c}** बार")

    # ================= TAB 6: 00-99 ALL NUMBERS & HARUF 100% ANALYSIS =================
    with tab6:
        st.subheader("💯 00 से 99 तक सभी नंबरों और हर्फ़ का All-Game 100% ऐतिहासिक विश्लेषण")
        st.info("यहाँ किसी भी गेम में कोई नंबर आने के बाद सभी 6 मार्केट में 00-99 तक की जोड़ियाँ और 0-9 तक के अंदर/बाहर हर्फ़ कितनी बार आए हैं, उसकी पूरी A-to-Z सूची दिखाई जाएगी।")
        
        c_t6_1, c_t6_2, c_t6_3 = st.columns(3)
        with c_t6_1:
            t6_game = st.selectbox("🎯 टारगेट गेम चुनें:", available_cols, index=available_cols.index('GALI') if 'GALI' in available_cols else 0, key="t6_game")
        with c_t6_2:
            t6_target = st.number_input("🔢 टारगेट नंबर दर्ज करें:", min_value=0, max_value=99, value=25, step=1, key="t6_num")
        with c_t6_3:
            t6_window = st.slider("📅 विंडो (कितने दिन के अंदर देखना है):", min_value=1, max_value=5, value=2, key="t6_win")

        valid_df_t6 = df.dropna(subset=[t6_game]).reset_index(drop=True)
        target_indices = valid_df_t6.index[valid_df_t6[t6_game].astype(int) == t6_target].tolist()
        total_target_hits = len(target_indices)

        if total_target_hits > 0:
            st.success(f"📊 **13 साल के डेटा में `{t6_game}` में `{t6_target:02d}` कुल `{total_target_hits}` बार आया है।**")

            all_market_hits = Counter()
            ander_haruf_hits = Counter()
            bahar_haruf_hits = Counter()

            guaranteed_list = []

            for idx in target_indices:
                for d in range(1, t6_window + 1):
                    win_idx = idx + d
                    if win_idx < len(valid_df_t6):
                        for m_col in available_cols:
                            if pd.notna(valid_df_t6.loc[win_idx, m_col]):
                                hit_num = int(valid_df_t6.loc[win_idx, m_col])
                                all_market_hits[hit_num] += 1
                                
                                # हर्फ़ काउंटिंग (अंदर और बाहर)
                                a_h, b_h = extract_haruf(hit_num)
                                if a_h is not None: ander_haruf_hits[a_h] += 1
                                if b_h is not None: bahar_haruf_hits[b_h] += 1

            # 1. जोड़ी टेबल (00 to 99)
            t6_table_data = []
            for n in range(100):
                cnt = all_market_hits.get(n, 0)
                status = "💯 Guaranteed / आया ही आया" if cnt >= total_target_hits else ("🔥 High Hit" if cnt > 0 else "❌ Never (0 Bar)")
                if cnt >= total_target_hits:
                    guaranteed_list.append(f"{n:02d}")
                
                t6_table_data.append({
                    "नंबर": f"{n:02d}",
                    "कुल बार आया (सभी 6 गेम मिलाकर)": cnt,
                    "स्टेटस": status,
                    "फैमिली": get_family_head(n)
                })

            df_t6_summary = pd.DataFrame(t6_table_data).sort_values(by="कुल बार आया (सभी 6 गेम मिलाकर)", ascending=False).reset_index(drop=True)

            c_g1, c_g2 = st.columns(2)
            with c_g1:
                st.markdown(f"💯 **100% Guaranteed Numbers (जो हर बार गिरे हैं):**")
                if guaranteed_list:
                    st.text_area("कॉपी करें (Guaranteed Numbers):", value=", ".join(guaranteed_list), height=80, key=f"t6_guar_txt_{t6_game}_{t6_target}_{t6_window}")
                else:
                    st.warning("कोई भी single नंबर 100% हर बार नहीं आया, लेकिन नीचे सबसे ज्यादा आने वाले नंबर मौजूद हैं।")
            
            with c_g2:
                top_3_t6 = df_t6_summary.head(3)
                top_3_str = ", ".join(top_3_t6["नंबर"].tolist())
                st.markdown(f"🔥 **Top 3 सबसे ज्यादा आने वाले नंबर:**")
                st.text_area("कॉपी करें (Top 3 Overall Hits):", value=top_3_str, height=80, key=f"t6_top3_txt_{t6_game}_{t6_target}_{t6_window}")

            st.markdown("---")
            st.subheader(f"📋 1. `{t6_game}` में `{t6_target:02d}` आने के {t6_window} दिन के अंदर 00 से 99 तक सभी नंबरों की लिस्ट:")
            st.dataframe(df_t6_summary, use_container_width=True)

            # ================= HARUF ANALYSIS (0 to 9) =================
            st.markdown("---")
            st.subheader(f"🔑 2. `{t6_game}` में `{t6_target:02d}` आने के बाद अंदर/बाहर हर्फ़ (0 से 9) का A-to-Z विश्लेषण:")

            guar_ander = [str(d) for d in range(10) if ander_haruf_hits.get(d, 0) >= total_target_hits]
            guar_bahar = [str(d) for d in range(10) if bahar_haruf_hits.get(d, 0) >= total_target_hits]

            c_h_g1, c_h_g2 = st.columns(2)
            with c_h_g1:
                st.markdown("💯 **100% Guaranteed अंदर हर्फ़ (Ander):**")
                if guar_ander:
                    st.success(f"🎯 अंदर हर बार पास हुए हर्फ़: **{', '.join(guar_ander)}**")
                else:
                    st.info("ℹ️ कोई भी अंदर का हर्फ़ 100% हर बार नहीं आया।")

            with c_h_g2:
                st.markdown("💯 **100% Guaranteed बाहर हर्फ़ (Bahar):**")
                if guar_bahar:
                    st.success(f"🎯 बाहर हर बार पास हुए हर्फ़: **{', '.join(guar_bahar)}**")
                else:
                    st.info("ℹ️ कोई भी बाहर का हर्फ़ 100% हर बार नहीं आया।")

            haruf_table_data = []
            for h in range(10):
                a_cnt = ander_haruf_hits.get(h, 0)
                b_cnt = bahar_haruf_hits.get(h, 0)
                tot_cnt = a_cnt + b_cnt
                haruf_table_data.append({
                    "हर्फ़ (Digit)": str(h),
                    "अंदर (Ander) कुल बार": a_cnt,
                    "बाहर (Bahar) कुल बार": b_cnt,
                    "कुल बार खुला (A+B)": tot_cnt,
                    "अंदर 100% Status": "💯 Yes" if a_cnt >= total_target_hits else "❌ No",
                    "बाहर 100% Status": "💯 Yes" if b_cnt >= total_target_hits else "❌ No"
                })

            df_haruf_summary = pd.DataFrame(haruf_table_data).sort_values(by="कुल बार खुला (A+B)", ascending=False).reset_index(drop=True)
            st.dataframe(df_haruf_summary, use_container_width=True)

        else:
            st.warning("⚠️ चुना गया नंबर 13 साल के रिकॉर्ड में नहीं मिला।")

    # ================= TAB 7: BEST 6-DIGIT CROSSING (NEXT DAY ONLY) =================
    with tab7:
        st.subheader("🎯 अगले दिन (+1 Day) के लिए सर्वश्रेष्ठ 6-अंकों की क्रॉसिंग (6-Digit Crossing)")
        st.info("यह टैब डेटा को स्कैन करके अगले ही दिन (+1 Day) छह के छह मार्केट में सबसे ज्यादा पास होने वाली 6 अंकों की क्रॉसिंग (36 जोड़ियाँ) को खुद ढूँढकर निकालता है।")
        
        c_t7_1, c_t7_2 = st.columns(2)
        with c_t7_1:
            t7_game = st.selectbox("🎯 टारगेट गेम चुनें:", available_cols, index=available_cols.index('GALI') if 'GALI' in available_cols else 0, key="t7_game")
        with c_t7_2:
            t7_target = st.number_input("🔢 टारगेट नंबर दर्ज करें:", min_value=0, max_value=99, value=25, step=1, key="t7_num")

        valid_df_t7 = df.dropna(subset=[t7_game]).reset_index(drop=True)
        target_indices_t7 = valid_df_t7.index[valid_df_t7[t7_game].astype(int) == t7_target].tolist()
        total_hits_t7 = len(target_indices_t7)

        if total_hits_t7 > 0:
            st.success(f"📊 **13 साल के डेटा में `{t7_game}` में `{t7_target:02d}` कुल `{total_hits_t7}` बार आया है।**")

            next_day_occurrences = []
            for idx in target_indices_t7:
                win_idx = idx + 1
                if win_idx < len(valid_df_t7):
                    day_nums = []
                    for m_col in available_cols:
                        if pd.notna(valid_df_t7.loc[win_idx, m_col]):
                            day_nums.append(int(valid_df_t7.loc[win_idx, m_col]))
                    next_day_occurrences.append(day_nums)

            best_crossing = None
            max_pass_count = -1
            guaranteed_crossings = []

            # 6 अंकों के सभी कॉम्बिनेशन चेक करने के लिए (10C6 = 210 पॉसिबिलिटी)
            for cb in combinations(range(10), 6):
                cb_set = set(cb)
                crossing_pairs = {d1 * 10 + d2 for d1 in cb_set for d2 in cb_set}
                
                pass_events = 0
                for day_nums in next_day_occurrences:
                    if any(num in crossing_pairs for num in day_nums):
                        pass_events += 1

                if pass_events > max_pass_count:
                    max_pass_count = pass_events
                    best_crossing = cb

                if pass_events >= total_hits_t7:
                    guaranteed_crossings.append(cb)

            st.markdown("---")
            c_cr1, c_cr2 = st.columns(2)
            
            with c_cr1:
                st.markdown("🔥 **सबसे बेस्ट 6-अंकों की क्रॉसिंग (Top Recommendation):**")
                if best_crossing:
                    digits_str = "".join([str(d) for d in sorted(best_crossing)])
                    c_pairs = sorted([f"{d1}{d2}" for d1 in best_crossing for d2 in best_crossing])
                    pairs_str = ", ".join(c_pairs)
                    
                    st.success(f"👑 **क्रॉसिंग अंक:** `{digits_str}` ({'x'.join(list(digits_str))})")
                    st.write(f"📈 **पास रिकॉर्ड:** `{total_hits_t7}` में से **`{max_pass_count}`** बार पास")
                    st.text_area("कॉपी करें (36 Cross Pairs):", value=pairs_str, height=120, key=f"txt_cr_best_{t7_game}_{t7_target}")

            with c_cr2:
                st.markdown("💯 **100% Guaranteed 6-Digit Crossings (जो हर बार पास हुई हैं):**")
                if guaranteed_crossings:
                    g_list_str = []
                    for g_cb in guaranteed_crossings:
                        g_str = "".join([str(d) for d in sorted(g_cb)])
                        g_list_str.append(g_str)
                    
                    st.success(f"🎯 100% पास होने वाली 6 अंकों की क्रॉसिंग अंक: **{', '.join(g_list_str)}**")
                    
                    first_g = guaranteed_crossings[0]
                    g_pairs = sorted([f"{d1}{d2}" for d1 in first_g for d2 in first_g])
                    st.text_area("कॉपी करें (100% Guaranteed Pairs - 36):", value=", ".join(g_pairs), height=120, key=f"txt_cr_guar_{t7_game}_{t7_target}")
                else:
                    st.info("ℹ️ कोई भी 6-अंकों की क्रॉसिंग 100% हर बार नहीं आई, लेकिन सबसे ज्यादा पास होने वाली क्रॉसिंग बाएँ (Left) बॉक्स में है।")

        else:
            st.warning("⚠️ चुना गया नंबर 13 साल के रिकॉर्ड में नहीं मिला।")
