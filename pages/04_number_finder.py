"""
=============================================================================
📱 ऐप का नाम: Advanced All-in-One Analytics & Pattern Engine
-----------------------------------------------------------------------------
💡 मुख्य विशेषताएं:
1. संतुलित पैटर्न क्रॉसिंग और हरूफ़ इंजन (Tab 1)
2. ऑडिटेड सिंगल डायरेक्ट नंबर इंजन (Tab 2)
3. पिछले महीने की गहराई से जांच / डेटा ऑडिट (Tab 3)
4. स्पेशल पैटर्न स्कैनर - ऑटोमैटिक (हर गेम के ताज़ा रिजल्ट पर आधारित) और मैन्युअल (Tab 4)
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse

# --- Streamlit Page Config ---
st.set_page_config(page_title="Advanced All-in-One Analytics & Dashboard", layout="wide")

st.title("🎯 All-in-One Game Analytics & Deep Pattern Engine")
st.write("संतुलित पैटर्न एल्गोरिथम, ऑडिटेड सिंगल इंजन और ऑटोमैटिक पैटर्न स्कैनर के साथ।")

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
        # डेटा क्लीनिंग: सभी गेम के कॉलम को नंबर फॉर्मेट में बदलना
        for c in available_cols:
            df[c] = pd.to_numeric(df[c], errors='coerce')

        st.sidebar.header("⚙️ एल्गोरिथम कंट्रोल (Formula Tuning)")
        recent_days = st.sidebar.slider(
            "हाल के कितने दिनों (रिकॉर्ड्स) को मुख्य आधार बनाएं?", 
            min_value=15, max_value=300, value=60, step=5,
            help="कम दिन रखने पर ताज़ा ट्रेंड दिखेगा।"
        )
        
        # 4 टैब बनाए गए हैं
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 1. Balanced Crossing & Haruf", 
            "🔥 2. Audited Single Direct Engine",
            "🔍 3. डेटा ऑडिट (पिछले महीने की जांच)",
            "⚡ 4. स्पेशल पैटर्न स्कैनर (Auto & Manual)"
        ])
        
        # ==========================================
        # TAB 1: BALANCED CROSSING & HARUF ENGINE
        # ==========================================
        with tab1:
            st.subheader(f"📊 संतुलित पैटर्न क्रॉसिंग (पिछले {recent_days} दिनों के ट्रेंड पर आधारित)")
            
            def analyze_balanced_crossing(df, column_name, window_size):
                vals = df[column_name].dropna().tolist()
                valid_vals = [int(v) for v in vals if 0 <= int(v) <= 99]
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
            
            def get_audited_single_direct_number(sub_df, column_name, window_size):
                vals = sub_df[column_name].dropna().tolist()
                valid_vals = [int(v) for v in vals if 0 <= int(v) <= 99]
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

                st.markdown("---")
                st.markdown("### 📅 पिछले 10 दिनों के सिंगल नंबर (Date-Wise Rolling Single Numbers Box)")
                history_game = st.selectbox("डेट-वाइज इतिहास देखने के लिए गेम चुनें:", available_cols, key="hist_game_select")
                date_col = next((c for c in df.columns if 'date' in c.lower() or 'tarik' in c.lower() or 'din' in c.lower() or 'day' in c.lower()), 'DATE')
                
                raw_full_series = df[history_game].dropna().tolist()
                if len(raw_full_series) >= 15:
                    past_10_lines = []
                    total_len = len(df)
                    start_idx = max(10, total_len - 10)
                    
                    for idx in range(start_idx, total_len):
                        sub_df = df.iloc[:idx]
                        res_past = get_audited_single_direct_number(sub_df, history_game, recent_days)
                        if res_past:
                            date_label = str(df.loc[idx, date_col]) if date_col in df.columns else f"Row {idx+1}"
                            actual_val = f"{int(df.loc[idx, history_game]):02d}" if pd.notna(df.loc[idx, history_game]) else "--"
                            line_str = f"Date: {date_label} | Actual: {actual_val} ➔ Single Predicted: {res_past['single_direct']}"
                            past_10_lines.append(line_str)
                    
                    st.code("\n".join(past_10_lines), language="text")
                else:
                    st.warning("पर्याप्त डेटा नहीं है।")

        # ==========================================
        # TAB 3: DEEP DATA & LAST MONTH AUDIT
        # ==========================================
        with tab3:
            st.subheader("🔍 पिछले महीने के रिजल्ट्स और अंकों की गहराई से जांच (Audit)")
            
            audit_col1, audit_col2 = st.columns(2)
            with audit_col1:
                selected_game = st.selectbox("गेम / लोकेशन चुनें:", available_cols, index=available_cols.index('FRBD') if 'FRBD' in available_cols else 0)
            with audit_col2:
                audit_days = st.selectbox("कितने दिनों का रिकॉर्ड देखना है?", [30, 60, 90, 180], index=0)
                
            raw_series = df[selected_game].dropna().tolist()
            clean_series = [int(v) for v in raw_series if 0 <= int(v) <= 99]
                    
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
                    st.dataframe(audit_df, use_container_width=True, hide_index=True)
                with c2:
                    st.bar_chart(pd.DataFrame({"गिनती": [digit_counts[d] for d in range(10)]}, index=[str(d) for d in range(10)]))
                    
                st.markdown(f"**📜 पिछले {len(last_n_vals)} असली रिजल्ट्स:**")
                st.code(", ".join([f"{v:02d}" for v in last_n_vals]), language="text")

        # ==========================================
        # TAB 4: SPECIAL PATTERN SCANNER (AUTO & MANUAL)
        # ==========================================
        with tab4:
            st.subheader("⚡ स्पेशल पैटर्न स्कैनर: ताज़ा और मैन्युअल नंबर आधारित अगला सिंगल")
            
            # यहाँ जानकारी या मदद बॉक्स जोड़ा गया है ताकि याद रहे यह टैब क्या काम करता है
            with st.expander("ℹ️ इस पैटर्न स्कैनर के काम करने का तरीका (How it Works)"):
                st.markdown("""
                * **ऑटोमैटिक स्कैनर (Auto-Scan):** यह हर गेम के सबसे आखिरी (Last) रिजल्ट को खुद पकड़कर, उसी गेम के पुराने 13 साल के इतिहास में चेक करता है कि उस नंबर के बाद सबसे पक्का सिंगल नंबर क्या आता है।
                * **मैन्युअल स्कैनर (Manual Search):** आप अपनी पसंद का कोई भी नंबर दर्ज करके हर गेम का अलग-अलग पैटर्न सेपरेट चेक कर सकते हैं।
                """)

            st.markdown("### 🔥 1. ऑटोमैटिक लास्ट रिजल्ट पैटर्न स्कैनर (Auto-Scan Last Results)")
            st.write("यहाँ CSV के हर गेम के आखिरी नंबर को स्वतः पकड़कर उसके अगले फिक्स सिंगल नंबर की स्कैनिंग की गई है:")

            auto_results = []
            for col in available_cols:
                valid_series = df[col].dropna()
                if not valid_series.empty:
                    last_val = int(valid_series.iloc[-1])
                    formatted_last = f"{last_val:02d}"
                    
                    game_next_nums = []
                    for r_idx in range(len(df) - 1):
                        val = df.loc[r_idx, col]
                        if pd.notna(val) and int(val) == last_val:
                            for skip in range(1, 4):
                                if r_idx + skip < len(df):
                                    nx_val = df.loc[r_idx + skip, col]
                                    if pd.notna(nx_val):
                                        game_next_nums.append(int(nx_val))
                    
                    if game_next_nums:
                        g_series = pd.Series(game_next_nums).value_counts()
                        best_n = g_series.index[0]
                        best_cnt = g_series.iloc[0]
                        top_3_str = ", ".join([f"{k:02d} ({v} बार)" for k, v in g_series.head(3).items()])
                        auto_results.append({
                            "लोकेशन / गेम": col,
                            "ताज़ा रिजल्ट (Last)": formatted_last,
                            "अगला बेस्ट सिंगल नंबर": f"🔥 {best_n:02d}",
                            "इतिहास फ्रीक्वेंसी": f"{best_cnt} बार",
                            "टॉप 3 संभावित नंबर": top_3_str
                        })
                    else:
                        auto_results.append({
                            "लोकेशन / गेम": col,
                            "ताज़ा रिजल्ट (Last)": formatted_last,
                            "अगला बेस्ट सिंगल नंबर": "डेटा पर्याप्त नहीं",
                            "इतिहास फ्रीक्वेंसी": "-",
                            "टॉप 3 संभावित नंबर": "-"
                        })

            if auto_results:
                res_df_auto = pd.DataFrame(auto_results)
                st.dataframe(res_df_auto, use_container_width=True, hide_index=True)
                
                st.markdown("**📋 सभी गेम के अगले सिंगल नंबर की कंबाइंड लाइन (कॉपी करने के लिए):**")
                valid_singles = [row['अगला बेस्ट सिंगल नंबर'].replace('🔥 ', '') for row in auto_results if '🔥' in row['अगला बेस्ट सिंगल नंबर']]
                st.code(", ".join(valid_singles), language="text")

            st.markdown("---")
            st.markdown("### 🔍 2. मैन्युअल नंबर चेक बॉक्स (अपनी पसंद का नंबर हर गेम में अलग-अलग जांचें)")
            
            manual_col1, manual_col2 = st.columns([2, 2])
            with manual_col1:
                target_num_input = st.text_input("कोई भी नंबर दर्ज करें (जैसे: 80 या 07):", value="80", key="manual_target_input")
            with manual_col2:
                st.info("💡 यह विकल्प आपकी मर्जी के नंबर को हर गेम के अपने सेपरेट इतिहास में ढूंढेगा।")

            if st.button("🔎 मैन्युअल स्कैन चलाएं (Run Manual Scan)", use_container_width=True):
                try:
                    target_num = int(target_num_input)
                    if 0 <= target_num <= 99:
                        formatted_target = f"{target_num:02d}"
                        st.success(f"📊 नंबर **{formatted_target}** के लिए हर गेम के सेपरेट इतिहास की स्कैनिंग:")

                        manual_game_results = []
                        for col in available_cols:
                            game_next_nums = []
                            for r_idx in range(len(df) - 1):
                                val = df.loc[r_idx, col]
                                if pd.notna(val) and int(val) == target_num:
                                    for skip in range(1, 4):
                                        if r_idx + skip < len(df):
                                            nx_val = df.loc[r_idx + skip, col]
                                            if pd.notna(nx_val):
                                                game_next_nums.append(int(nx_val))
                            
                            if game_next_nums:
                                g_series = pd.Series(game_next_nums).value_counts()
                                best_n = g_series.index[0]
                                best_cnt = g_series.iloc[0]
                                top_3_str = ", ".join([f"{k:02d} ({v} बार)" for k, v in g_series.head(3).items()])
                                manual_game_results.append({
                                    "लोकेशन / गेम": col,
                                    f"नंबर {formatted_target} के बाद बेस्ट सिंगल": f"🔥 {best_n:02d}",
                                    "फ्रीक्वेंसी": f"{best_cnt} बार",
                                    "टॉप 3 संभावित नंबर": top_3_str
                                })
                            else:
                                manual_game_results.append({
                                    "लोकेशन / गेम": col,
                                    f"नंबर {formatted_target} के बाद बेस्ट सिंगल": "डाटा नहीं",
                                    "फ्रीक्वेंसी": "-",
                                    "टॉप 3 संभावित नंबर": "-"
                                })

                        if manual_game_results:
                            res_df_man = pd.DataFrame(manual_game_results)
                            st.dataframe(res_df_man, use_container_width=True, hide_index=True)
                            
                            st.markdown(f"**📋 नंबर {formatted_target} के बाद सभी गेम के अगले सिंगल की लाइन:**")
                            valid_man_singles = [row[f'नंबर {formatted_target} के बाद बेस्ट सिंगल'].replace('🔥 ', '') for row in manual_game_results if '🔥' in row[f'नंबर {formatted_target} के बाद बेस्ट सिंगल']]
                            st.code(", ".join(valid_man_singles), language="text")

                    else:
                        st.error("कृपया 00 से 99 के बीच का कोई वैध नंबर दर्ज करें।")
                except ValueError:
                    st.error("कृपया नंबर सही फॉर्मेट में दर्ज करें।")

    else:
        st.error("CSV फ़ाइल में DB, SG, FRBD, GZBD, GALI, DSWR में से कोई भी कॉलम नहीं मिला!")
else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर दी गई जगह पर अपनी CSV फ़ाइल अपलोड करें।")
