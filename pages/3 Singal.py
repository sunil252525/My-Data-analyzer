import streamlit as st
import pandas as pd
from collections import Counter

st.set_page_config(page_title="Ultimate 13-Year Pattern & Target Detector", layout="wide")

st.title("🎯 Ultimate 13-Year Master Pattern & Target Detector v3.0")

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
    """अंकों का जोड़ (Sum)"""
    try:
        n = int(num)
        return (n // 10) + (n % 10)
    except: return None

def get_odd_even_type(num):
    """Even-Even, Odd-Odd, Odd-Even प्रकार"""
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

    # मुख्य टैब्स
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 1. टारगेट सर्च", 
        "🔄 2. चाल & हर्फ़ पैटर्न", 
        "🔴 3. हॉट & कोल्ड हीटमैप", 
        "👑 4. ऑटो-पैटर्न चेज़र",
        "⚖️ 5. जोड़ & Odd/Even एनालिसिस"
    ])

    # ================= TAB 1: TARGET REPEAT (UPDATED WITH ALL-GAME BREAKDOWN) =================
    with tab1:
        st.subheader("⚙️ टारगेट सर्च सेटिंग्स:")
        col_sel1, col_sel2, col_sel3 = st.columns(3)
        with col_sel1:
            selected_game = st.selectbox("🎯 गेम चुनें (जिसमें टारगेट देखना है):", available_cols, index=available_cols.index('GALI') if 'GALI' in available_cols else 0, key="t1_game")
        with col_sel2:
            target_number = st.number_input("🔢 टारगेट नंबर दर्ज करें:", min_value=0, max_value=99, value=25, step=1, key="t1_num")
        with col_sel3:
            window_days = st.slider("📅 विंडो (कितने दिन के अंदर):", min_value=1, max_value=5, value=2, key="t1_win")

        st.markdown("---")
        
        # 1. चुनी गई गेम में टारगेट नंबर की ऐतिहासिक घटनाएँ
        logs, next_day_list, window_list = analyze_target_occurrences(df, selected_game, target_number, window_days)

        if logs:
            st.success(f"📊 **13 साल के डेटा में `{selected_game}` में `{target_number:02d}` कुल `{len(logs)}` बार आया है।**")
            
            # Top 3 रिपीट सिंगल नंबर
            single_counts = Counter(window_list)
            top_3_tuples = single_counts.most_common(3)
            top_3_singles = [item[0] for item in top_3_tuples]
            top_3_singles_str = ", ".join([f"{n:02d}" for n in top_3_singles])

            # Top 1 सबसे मुख्य (Single Top) फैमिली निकालना
            family_counts = Counter([get_family_head(num) for num in window_list])
            top_1_family_tuple = family_counts.most_common(1)
            
            if top_1_family_tuple:
                top_fam_head, top_fam_total_count = top_1_family_tuple[0]
                top_fam_pairs = get_family(top_fam_head)
                top_fam_pairs_str = ", ".join([f"{n:02d}" for n in top_fam_pairs])

                # चारों प्रमुख गेमों (GALI, DSWR, FRBD, GZBD) में इस 1 फैमिली का ब्रेकअप निकालना
                # Target नंबर आने की तारीख/रो के अगले window_days के दौरान अन्य गेमों में स्कैन
                main_games = ['GALI', 'DSWR', 'FRBD', 'GZBD']
                game_breakdown = {g: 0 for g in main_games}
                
                valid_indices = df[selected_game].dropna().index[df[selected_game].dropna().astype(float) == target_number].tolist()
                
                for idx in valid_indices:
                    for d in range(1, window_days + 1):
                        target_idx = idx + d
                        if target_idx < len(df):
                            for g in main_games:
                                if g in df.columns and pd.notna(df.loc[target_idx, g]):
                                    val = int(df.loc[target_idx, g])
                                    if val in top_fam_pairs:
                                        game_breakdown[g] += 1

            col_box1, col_box2 = st.columns(2)
            with col_box1:
                st.markdown(f"🔥 **Top 3 रिपीट सिंगल नंबर:**")
                st.text_area("कॉपी करें (Single Repeat Numbers):", value=top_3_singles_str, height=100, key=f"txt_single_{selected_game}_{target_number}_{window_days}")
                for num, count in top_3_tuples: st.write(f"- नंबर **`{num:02d}`**: कुल **{count}** बार आया")

            with col_box2:
                st.markdown(f"👑 **Top 1 सबसे ज्यादा रिपीट फैमिली की जोड़ियाँ:**")
                if top_1_family_tuple:
                    st.text_area("कॉपी करें (Single Top Family Pairs):", value=top_fam_pairs_str, height=100, key=f"txt_top1_family_{selected_game}_{target_number}_{window_days}")
                    st.write(f"🏆 **`{top_fam_head:02d}`** की फैमिली: कुल **{top_fam_total_count}** बार पास हुई")
                    
                    st.markdown("🎯 **यह फैमिली 2 दिन के अंदर किस-किस गेम में कितनी बार आई:**")
                    for g_name, g_cnt in game_breakdown.items():
                        st.write(f" - **{g_name}**: `{g_cnt}` बार")
                else:
                    st.info("कोई फैमिली डेटा नहीं मिला।")

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

    # ================= TAB 3: HOT & COLD HEATMAP (FIXED) =================
    with tab3:
        st.subheader("🔴🔵 100 नंबरों का फ्रीक्वेंसी हीटमैप (Hot & Cold Chart)")
        heat_game = st.selectbox("🎯 गेम चुनें:", available_cols, key="heat_game")
        recent_scan_days = st.slider("📅 कितने हालिया दिनों में देखना है:", min_value=10, max_value=365, value=60, key="heat_days")
        
        # ⚠️ यहाँ reset_index(drop=True) जोड़ा गया है ताकि ताज़ा डेटा सही से फ़िल्टर हो
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

else:
    st.info("👈 बाएँ साइडबार से 13 साल की CSV फ़ाइल अपलोड करके शुरू करें।")
