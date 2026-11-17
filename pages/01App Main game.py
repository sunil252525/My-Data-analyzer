import streamlit as st
import pandas as pd
import urllib.parse

# --- Streamlit Page Config ---
st.set_page_config(page_title="Advanced All-in-One Analytics & Diagnostic Engine", layout="wide")

st.title("🎯 All-in-One Game Analytics & Deep Diagnostic Dashboard")
st.write("संतुलित पैटर्न एल्गोरिथम, ऑडिटेड सिंगल इंजन और पिछले 10 दिनों के डेट-वाइज सिंगल नंबर रिकॉर्ड के साथ।")

# --- RASHI & FAMILY HELPER ---
RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi_digit(d):
    return RASHI_MAP.get(int(d), int(d))

def get_family_numbers(num):
    try:
        num = int(num)
        d1, d2 = num // 10, num % 10
        r1, r2 = get_rashi_digit(d1), get_rashi_digit(d2)
        fam = set()
        for a, b in [(d1, d2), (d1, r2), (r1, d2), (r1, r2)]:
            fam.add(a * 10 + b)
            fam.add(b * 10 + a)
        return list(fam)
    except:
        return []

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("📂 कृपया अपनी CSV फ़ाइल यहाँ अपलोड करें", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    if available_cols:
        st.sidebar.header("⚙️ एल्गोरिथम कंट्रोल (Formula Tuning)")
        recent_days = st.sidebar.slider(
            "हाल के कितने दिनों (रिकॉर्ड्स) को मुख्य आधार बनाएं?", 
            min_value=15, max_value=180, value=45, step=5,
            help="कम दिन रखने पर ताज़ा ट्रेंड दिखेगा और पुराने अंक बार-बार रिपीट नहीं होंगे।"
        )
        
        tab1, tab2, tab3 = st.tabs([
            "🎯 1. Balanced Crossing & Haruf Engine", 
            "🔥 2. Audited Single Direct Number Engine (No Palat)",
            "🔍 3. पिछले महीने की गहराई से जांच (Data Audit)"
        ])
        
        # ==========================================
        # TAB 1: BALANCED CROSSING & HARUF ENGINE
        # ==========================================
        with tab1:
            st.subheader(f"📊 संतुलित पैटर्न क्रॉसिंग (पिछले {recent_days} दिनों के ट्रेंड पर आधारित)")
            
            def analyze_balanced_crossing(df, column_name, window_size):
                vals = df[column_name].dropna().tolist()
                valid_vals = []
                for x in vals:
                    try:
                        val = int(x)
                        if 0 <= val <= 99:
                            valid_vals.append(val)
                    except:
                        continue
                if len(valid_vals) < 10:
                    return None

                last_num = valid_vals[-1]
                haruf_scores = {d: 0.0 for d in range(10)}
                
                recent_slice = valid_vals[-window_size:]
                for idx, num in enumerate(recent_slice):
                    recency_boost = 1.0 + (idx / len(recent_slice)) * 1.5
                    haruf_scores[num // 10] += recency_boost
                    haruf_scores[num % 10] += recency_boost

                follow_up_count = 0
                for i in range(len(valid_vals) - 2):
                    if valid_vals[i] == last_num:
                        follow_up_count += 1
                        f1 = valid_vals[i + 1]
                        f2 = valid_vals[i + 2]
                        haruf_scores[f1 // 10] += 2.5
                        haruf_scores[f1 % 10] += 2.5
                        haruf_scores[f2 // 10] += 1.5
                        haruf_scores[f2 % 10] += 1.5

                ranked_harufs = sorted(haruf_scores.keys(), key=lambda x: haruf_scores[x], reverse=True)
                single_haruf = ranked_harufs[0]
                top_4_harufs = sorted(ranked_harufs[:4])
                top_6_harufs = sorted(ranked_harufs[:6])

                return {
                    "last_num": f"{last_num:02d}",
                    "single_haruf": str(single_haruf),
                    "haruf_4_str": ", ".join(map(str, top_4_harufs)),
                    "haruf_6_str": ", ".join(map(str, top_6_harufs)),
                    "single_h_int": single_haruf,
                    "matches_found": follow_up_count
                }

            analysis_results = []
            full_box_messages = []
            all_unique_harufs = set()

            for col in available_cols:
                res = analyze_balanced_crossing(df, col, recent_days)
                if res:
                    analysis_results.append({
                        "लोकेशन / गेम": col,
                        "🎯 ताज़ा रिज़ल्ट": res["last_num"],
                        "👑 सिंगल हरूफ़ (1 Haruf)": f"🔥 {res['single_haruf']} (अंदर/बाहर)",
                        "⚡ 4 हरूफ़ क्रॉसिंग": res["haruf_4_str"],
                        "🔥 6 हरूफ़ क्रॉसिंग": res["haruf_6_str"],
                        "📈 हिस्ट्री मैच": f"{res['matches_found']} बार"
                    })
                    all_unique_harufs.add(res["single_h_int"])
                    game_msg = (
                        f"🎯 *{col}* (Last: {res['last_num']})\n"
                        f"👑 सिंगल हरूफ़: *{res['single_haruf']}* (अंदर/बाहर)\n"
                        f"⚡ 4 हरूफ़: [{res['haruf_4_str']}]\n"
                        f"🔥 6 हरूफ़: [{res['haruf_6_str']}]"
                    )
                    full_box_messages.append(game_msg)

            if analysis_results:
                res_df_1 = pd.DataFrame(analysis_results)
                st.dataframe(res_df_1, use_container_width=True, hide_index=True)
                
                st.markdown("📋 **एक्सेल के लिए डेटा (यहाँ से कॉपी करें):**")
                tsv_data_1 = res_df_1.to_csv(sep='\t', index=False)
                st.text_area("Tab 1 Excel Data", value=tsv_data_1, height=150, key="excel_tab1")

                sorted_unique = sorted(list(all_unique_harufs))
                unique_crossing_str = ", ".join(map(str, sorted_unique))
                st.markdown("### 🔗 सभी गेम के सिंगल हरूफ़ की संयुक्त क्रॉसिंग (Unique Harufs Crossing)")
                st.code(unique_crossing_str, language="text")
                
                st.markdown("---")
                full_whatsapp_text = "📊 *COMPLETE DAILY ANALYTICS REPORT* 📊\n\n" + "\n\n---\n\n".join(full_box_messages) + f"\n\n🔗 *Unique Harufs Crossing:* [{unique_crossing_str}]"
                encoded_full_msg = urllib.parse.quote(full_whatsapp_text)
                wa_full_url = f"https://api.whatsapp.com/send?text={encoded_full_msg}"
                st.markdown(
                    f'<a href="{wa_full_url}" target="_blank">'
                    f'<button style="background-color:#25D366; color:white; border:none; padding:12px 20px; '
                    f'font-size:16px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%;">'
                    f'📲 क्रॉसिंग समरी बॉक्स WhatsApp पर भेजें (Share Crossing Box)'
                    f'</button></a>',
                    unsafe_allow_html=True
                )

        # ==========================================
        # TAB 2: AUDITED SINGLE DIRECT NUMBER ENGINE
        # ==========================================
        with tab2:
            st.subheader("🎯 100% ऑडिटेड सिंगल नंबर डायरेक्ट इंजन (Smart Fallback & No Palat)")
            st.write("इस इंजन में सटीक इतिहास, फैमिली पैटर्न और ट्रेंड बूस्ट के साथ-साथ नीचे **पिछले 10 दिनों का डेट-वाइज सिंगल नंबर रिकॉर्ड बॉक्स** भी जोड़ा गया है।")
            
            def get_audited_single_direct_number(sub_df, column_name, window_size):
                vals = sub_df[column_name].dropna().tolist()
                valid_vals = []
                for x in vals:
                    try:
                        v = int(x)
                        if 0 <= v <= 99:
                            valid_vals.append(v)
                    except:
                        continue
                if len(valid_vals) < 10:
                    return None

                last_num = valid_vals[-1]
                num_scores = {n: 1.0 for n in range(100)}
                
                for idx, num in enumerate(valid_vals[-window_size:]):
                    num_scores[num] += (0.1 + (idx / window_size) * 0.4)

                direct_matches = 0
                for i in range(len(valid_vals) - 1):
                    if valid_vals[i] == last_num:
                        direct_matches += 1
                        nxt = valid_vals[i + 1]
                        num_scores[nxt] += 6.0
                        
                for i in range(len(valid_vals) - 2):
                    if valid_vals[i] == last_num:
                        nxt2 = valid_vals[i + 2]
                        num_scores[nxt2] += 3.5

                if direct_matches < 3:
                    fam_nums = get_family_numbers(last_num)
                    for fn in fam_nums:
                        if fn in num_scores:
                            num_scores[fn] += 4.0

                in_c = {d: 0.0 for d in range(10)}
                out_c = {d: 0.0 for d in range(10)}
                for num in valid_vals[-window_size:]:
                    in_c[num // 10] += 1.0
                    out_c[num % 10] += 1.0
                
                best_in = max(in_c, key=in_c.get)
                best_out = max(out_c, key=out_c.get)
                crossing_num = best_in * 10 + best_out
                num_scores[crossing_num] += 5.0

                best_single_num = max(num_scores, key=num_scores.get)
                
                return {
                    "last_num": f"{last_num:02d}",
                    "single_direct": f"{best_single_num:02d}",
                    "score": round(num_scores[best_single_num], 1),
                    "matches": direct_matches
                }

            single_results = []
            wa_msg_lines = []

            for col in available_cols:
                res = get_audited_single_direct_number(df, col, recent_days)
                if res:
                    single_results.append({
                        "लोकेशन / गेम": col,
                        "🎯 ताज़ा रिज़ल्ट": res["last_num"],
                        "👑 1 सिंगल नंबर (No Palat)": f"🔥 {res['single_direct']} (100)",
                        "📊 इतिहास मैच": f"{res['matches']} बार",
                        "⭐ स्कोर": f"{res['score']} pts"
                    })
                    wa_msg_lines.append(f"• *{col}* (Last: {res['last_num']}) ➔ Single: *{res['single_direct']}* (100)")

            if single_results:
                res_df_2 = pd.DataFrame(single_results)
                st.dataframe(res_df_2, use_container_width=True, hide_index=True)
                
                st.markdown("📋 **एक्सेल के लिए डेटा (यहाँ से कॉपी करें):**")
                tsv_data_2 = res_df_2.to_csv(sep='\t', index=False)
                st.text_area("Tab 2 Excel Data", value=tsv_data_2, height=150, key="excel_tab2")

                st.markdown("### 📋 सभी गेम का 1-1 सिंगल नंबर (Copy / Direct Line)")
                direct_line_text = ", ".join([f"{r['👑 1 सिंगल नंबर (No Palat)'].split()[1]}" for r in single_results])
                st.code(direct_line_text, language="text")

                # ==========================================================
                # NEW ADDITION: PAST 10 DAYS DATE-WISE SINGLE NUMBERS BOX
                # ==========================================================
                st.markdown("---")
                st.markdown("### 📅 पिछले 10 दिनों के सिंगल नंबर (Date-Wise Rolling Single Numbers Box)")
                st.write("यहाँ किसी भी गेम के लिए पिछले 10 रिकॉर्ड्स/दिनों के हिसाब से गणना किए गए सिंगल नंबर डेट-वाइज (एक के बाद एक लाइन में) दिए गए हैं:")

                # गेम चुनने के लिए सलेक्ट बॉक्स
                history_game = st.selectbox("डेट-वाइज इतिहास देखने के लिए गेम चुनें:", available_cols, key="hist_game_select")
                
                # चेक करें कि क्या CSV में कोई 'Date' या 'Tarik' कॉलम है
                date_col = next((c for c in df.columns if 'date' in c.lower() or 'tarik' in c.lower() or 'din' in c.lower() or 'day' in c.lower()), None)
                
                raw_full_series = df[history_game].dropna().tolist()
                if len(raw_full_series) >= 15:
                    past_10_lines = []
                    # पिछले 10 इंडेक्स पर लूप चलाएं
                    total_len = len(df)
                    start_idx = max(10, total_len - 10)
                    
                    for idx in range(start_idx, total_len):
                        sub_df = df.iloc[:idx] # उस दिन तक का डेटा
                        res_past = get_audited_single_direct_number(sub_df, history_game, recent_days)
                        if res_past:
                            # यदि डेट कॉलम है तो डेट उठाएं, नहीं तो रिकॉर्ड नंबर/इंडेक्स दिखाएं
                            date_label = str(df.loc[idx, date_col]) if date_col and date_col in df.columns else f"Day / Row {idx+1}"
                            actual_val = f"{int(df.loc[idx, history_game]):02d}" if pd.notna(df.loc[idx, history_game]) else "--"
                            
                            line_str = f"Date/Row: {date_label} | Actual: {actual_val} ➔ Single Predicted: {res_past['single_direct']}"
                            past_10_lines.append(line_str)
                    
                    past_10_text = "\n".join(past_10_lines)
                    st.code(past_10_text, language="text")
                else:
                    st.warning("इस गेम में पिछले 10 दिनों की गणना के लिए पर्याप्त डेटा उपलब्ध नहीं है।")

                st.markdown("---")
                wa_text = "🎯 *TODAY SINGLE DIRECT NUMBERS (AUDITED)* 🎯\n\n" + "\n".join(wa_msg_lines)
                encoded_msg = urllib.parse.quote(wa_text)
                wa_url = f"https://api.whatsapp.com/send?text={encoded_msg}"
                st.markdown(
                    f'<a href="{wa_url}" target="_blank">'
                    f'<button style="background-color:#25D366; color:white; border:none; padding:12px 20px; '
                    f'font-size:16px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%;">'
                    f'📲 केवल सिंगल नंबर WhatsApp पर भेजें (Share Single Numbers)'
                    f'</button></a>',
                    unsafe_allow_html=True
                )

        # ==========================================
        # TAB 3: DEEP DATA & LAST MONTH AUDIT
        # ==========================================
        with tab3:
            st.subheader("🔍 पिछले महीने के रिजल्ट्स और अंकों की गहराई से जांच (Audit)")
            st.write("यहाँ आप देख सकते हैं कि किसी भी गेम में पिछले 30 दिनों (1 महीना) में असल में क्या-क्या आया है।")
            
            audit_col1, audit_col2 = st.columns(2)
            with audit_col1:
                selected_game = st.selectbox("गेम / लोकेशन चुनें:", available_cols, index=available_cols.index('FRBD') if 'FRBD' in available_cols else 0)
            with audit_col2:
                audit_days = st.selectbox("कितने दिनों का रिकॉर्ड देखना है?", [30, 60, 90, 180], index=0)
                
            raw_series = df[selected_game].dropna().tolist()
            clean_series = []
            for x in raw_series:
                try:
                    v = int(x)
                    if 0 <= v <= 99:
                        clean_series.append(v)
                except:
                    continue
                    
            if clean_series:
                last_n_vals = clean_series[-audit_days:]
                digit_counts = {d: 0 for d in range(10)}
                for num in last_n_vals:
                    digit_counts[num // 10] += 1
                    digit_counts[num % 10] += 1
                    
                audit_df = pd.DataFrame({
                    "अंक (Haruf)": [str(d) for d in range(10)],
                    "पिछले दिनों में कुल बार आया": [digit_counts[d] for d in range(10)],
                    "प्रतिशत (%)": [round((digit_counts[d] / (len(last_n_vals) * 2)) * 100, 1) for d in range(10)]
                }).sort_values(by="पिछले दिनों में कुल बार आया", ascending=False)
                
                c1, c2 = st.columns([1.2, 1])
                with c1:
                    st.markdown(f"**📊 {selected_game} में पिछले {len(last_n_vals)} रिजल्ट्स में अंकों की असली स्थिति:**")
                    st.dataframe(audit_df, use_container_width=True, hide_index=True)
                    
                with c2:
                    st.markdown(f"**📈 {selected_game} हरूफ़ ग्राफ (Visual Check):**")
                    chart_data = pd.DataFrame({
                        "अंक": [str(d) for d in range(10)],
                        "गिनती": [digit_counts[d] for d in range(10)]
                    }).set_index("अंक")
                    st.bar_chart(chart_data)
                    
                st.markdown(f"**📜 {selected_game} के पिछले {len(last_n_vals)} असली रिजल्ट्स (क्रम अनुसार):**")
                formatted_history = ", ".join([f"{v:02d}" for v in last_n_vals])
                st.code(formatted_history, language="text")
    else:
        st.error("CSV फ़ाइल में DB, SG, FRBD, GZBD, GALI, DSWR में से कोई भी कॉलम नहीं मिला!")
else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर दी गई जगह पर अपनी CSV फ़ाइल अपलोड करें।")
    
