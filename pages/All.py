import streamlit as st
import pandas as pd
import urllib.parse

# --- Streamlit Page Config ---
st.set_page_config(page_title="Advanced All-in-One Analytics & Backtesting Engine", layout="wide")

st.title("🎯 All-in-One Game Analytics & Automatic Backtesting Engine")
st.write("यहाँ दो टैब दिए गए हैं: पहला **क्रॉसिंग इंजन** के लिए और दूसरा **सिंगल डायरेक्ट नंबर इंजन** के लिए। हर टैब में पीछे की तारीखों (जैसे 7 तारीख, 8 तारीख आदि) का ऑटोमैटिक पास/फेल रिकॉर्ड दिखाया गया है।")

# --- FILE UPLOADER (SHARED FOR BOTH TABS) ---
uploaded_file = st.file_uploader("📂 कृपया अपनी CSV फ़ाइल यहाँ अपलोड करें", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # डेट कॉलम की पहचान करना
    date_col = None
    for c in df.columns:
        c_lower = c.lower()
        if 'date' in c_lower or 'din' in c_lower or 'दिनांक' in c or 'tarikh' in c_lower:
            date_col = c
            break

    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    if available_cols:
        # दो ही टैब बनाए गए हैं
        tab1, tab2 = st.tabs([
            "🎯 1. Complete Crossing Engine & Past Backtest", 
            "🔥 2. Single Direct Number Engine & Past Backtest"
        ])
        
        # ==========================================
        # TAB 1: COMPLETE CROSSING & HARUF ENGINE
        # ==========================================
        with tab1:
            st.subheader("📊 ऐतिहासिक डेटा और फॉलो-अप पैटर्न के आधार पर क्रॉसिंग")
            
            def analyze_best_crossing_and_haruf(sub_df, column_name):
                vals = sub_df[column_name].dropna().tolist()
                valid_vals = []
                
                for x in vals:
                    try:
                        val = int(x)
                        if 0 <= val <= 99:
                            valid_vals.append(val)
                    except:
                        continue
                        
                if len(valid_vals) < 5:
                    return None

                last_num = valid_vals[-1]
                haruf_scores = {d: 0 for d in range(10)}
                
                total_len = len(valid_vals)
                for idx, num in enumerate(valid_vals):
                    weight = 1 + (idx / total_len)
                    haruf_scores[num // 10] += weight
                    haruf_scores[num % 10] += weight

                follow_up_harufs = []
                for i in range(len(valid_vals) - 2):
                    if valid_vals[i] == last_num:
                        f1 = valid_vals[i + 1]
                        f2 = valid_vals[i + 2]
                        follow_up_harufs.extend([f1 // 10, f1 % 10, f2 // 10, f2 % 10])

                for h in follow_up_harufs:
                    if 0 <= h <= 9:
                        haruf_scores[h] += 3.5

                ranked_harufs = sorted(haruf_scores.keys(), key=lambda x: haruf_scores[x], reverse=True)
                
                single_haruf = ranked_harufs[0]
                top_4_harufs = sorted(ranked_harufs[:4])
                top_6_harufs = sorted(ranked_harufs[:6])

                return {
                    "last_num": f"{last_num:02d}",
                    "single_haruf": str(single_haruf),
                    "haruf_4_str": ", ".join(map(str, top_4_harufs)),
                    "haruf_6_str": ", ".join(map(str, top_6_harufs)),
                    "top_4_list": top_4_harufs,
                    "top_6_list": top_6_harufs
                }

            # आज का ताज़ा विश्लेषण
            analysis_results = []
            full_box_messages = []

            for col in available_cols:
                res = analyze_best_crossing_and_haruf(df, col)
                if res:
                    analysis_results.append({
                        "लोकेशन / गेम": col,
                        "🎯 ताज़ा रिज़ल्ट": res["last_num"],
                        "👑 सिंगल हरूफ़ (1 Haruf)": f"🔥 {res['single_haruf']} (अंदर/बाहर)",
                        "⚡ 4 हरूफ़ क्रॉसिंग": res["haruf_4_str"],
                        "💡 4-हरूफ़ जोड़ियाँ": "16 जोड़ियाँ (4x4)",
                        "🔥 6 हरूफ़ क्रॉसिंग": res["haruf_6_str"],
                        "📊 6-हरूफ़ जोड़ियाँ": "36 जोड़ियाँ (6x6)"
                    })
                    
                    game_msg = (
                        f"🎯 *{col}* (Last: {res['last_num']})\n"
                        f"👑 सिंगल हरूफ़: *{res['single_haruf']}* (अंदर/बाहर)\n"
                        f"⚡ 4 हरूफ़ (16 जोड़ियाँ): [{res['haruf_4_str']}]\n"
                        f"🔥 6 हरूफ़ (36 जोड़ियाँ): [{res['haruf_6_str']}]"
                    )
                    full_box_messages.append(game_msg)

            if analysis_results:
                st.dataframe(pd.DataFrame(analysis_results), use_container_width=True, hide_index=True)
                
                st.markdown("---")
                full_whatsapp_text = "📊 *COMPLETE DAILY ANALYTICS REPORT* 📊\n\n" + "\n\n---\n\n".join(full_box_messages)
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

            # --- ऑटोमैटिक पास्ट बैक-टेस्टिंग (पीछे के रिकॉर्ड की जाँच) ---
            st.markdown("---")
            st.subheader("📈 क्रॉसिंग इंजन ऑटोमैटिक पास्ट बैक-टेस्टिंग (Date-wise Pass/Fail)")
            st.write("यहाँ ऐप खुद पीछे के दिनों (जैसे 7 तारीख, 8 तारीख आदि) में जाकर चेक कर रहा है कि उस दिन क्या प्रेडिक्शन था और रिजल्ट पास हुआ या फेल:")
            
            sel_game_c = st.selectbox("गेम चुनें (पासिंग रिकॉर्ड देखने के लिए):", available_cols, key="backtest_c")
            
            if sel_game_c:
                dates_list = df[date_col].tolist() if date_col and date_col in df.columns else [f"Row {i+1}" for i in range(len(df))]
                backtest_data_c = []
                
                # कम से कम 10 दिनों का डेटा होने पर ही बैकटेस्ट शुरू करें
                for i in range(10, len(df)):
                    sub_df = df.iloc[:i] # i तारीख तक का डेटा
                    res_past = analyze_best_crossing_and_haruf(sub_df, sel_game_c)
                    
                    if res_past:
                        try:
                            actual_val = int(df.loc[i, sel_game_c])
                            if 0 <= actual_val <= 99:
                                act_str = f"{actual_val:02d}"
                                act_in = int(act_str[0])
                                act_out = int(act_str[1])
                                
                                top4 = res_past["top_4_list"]
                                top6 = res_past["top_6_list"]
                                single_h = int(res_past["single_haruf"])
                                
                                # पासिंग चेक
                                single_pass = "✅ PASS" if (single_h == act_in or single_h == act_out) else "❌ FAIL"
                                h4_pass = "✅ PASS" if (act_in in top4 or act_out in top4) else "❌ FAIL"
                                h6_pass = "✅ PASS" if (act_in in top6 or act_out in top6) else "❌ FAIL"
                                
                                row_date = dates_list[i] if i < len(dates_list) else f"Row {i+1}"
                                
                                backtest_data_c.append({
                                    "📅 दिनांक (Date)": row_date,
                                    "लोकेशन": sel_game_c,
                                    "वास्तविक रिज़ल्ट": act_str,
                                    "सिंगल हरूफ़": res_past["single_haruf"],
                                    "सिंगल स्टेटस": single_pass,
                                    "4 हरूफ़ पासिंग": h4_pass,
                                    "6 हरूफ़ पासिंग": h6_pass
                                })
                        except:
                            continue
                
                if backtest_data_c:
                    st.dataframe(pd.DataFrame(backtest_data_c[::-1]), use_container_width=True, hide_index=True)
                else:
                    st.warning("बैकटेस्ट के लिए पर्याप्त डेटा उपलब्ध नहीं है।")

        # ==========================================
        # TAB 2: SINGLE DIRECT NUMBER ENGINE
        # ==========================================
        with tab2:
            st.subheader("🎯 100% सिंगल नंबर डायरेक्ट इंजन (No Palat)")
            
            def get_best_single_direct_number(sub_df, column_name):
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
                
                in_haruf_counts = {d: 0 for d in range(10)}
                out_haruf_counts = {d: 0 for d in range(10)}
                for num in valid_vals[-50:]:
                    in_haruf_counts[num // 10] += 1
                    out_haruf_counts[num % 10] += 1
                    
                top_in_haruf = max(in_haruf_counts.keys(), key=lambda x: in_haruf_counts[x])
                top_out_haruf = max(out_haruf_counts.keys(), key=lambda x: out_haruf_counts[x])
                
                num_scores = {n: 0.0 for n in range(100)}
                
                for i in range(len(valid_vals) - 1):
                    if valid_vals[i] == last_num:
                        nxt = valid_vals[i + 1]
                        num_scores[nxt] += 5.0
                        
                for i in range(len(valid_vals) - 2):
                    if valid_vals[i] == last_num:
                        nxt2 = valid_vals[i + 2]
                        num_scores[nxt2] += 3.0
                        
                crossing_best = top_in_haruf * 10 + top_out_haruf
                num_scores[crossing_best] += 4.0
                
                for n in valid_vals[-30:]:
                    num_scores[n] += 0.5
                    
                best_single_num = max(num_scores.keys(), key=lambda x: num_scores[x])
                
                return {
                    "last_num": f"{last_num:02d}",
                    "single_direct": f"{best_single_num:02d}",
                    "score": round(num_scores[best_single_num], 1),
                    "num_int": best_single_num
                }

            single_results = []
            wa_msg_lines = []

            for col in available_cols:
                res = get_best_single_direct_number(df, col)
                if res:
                    single_results.append({
                        "लोकेशन / गेम": col,
                        "🎯 ताज़ा रिज़ल्ट": res["last_num"],
                        "👑 1 सिंगल नंबर (No Palat)": f"🔥 {res['single_direct']} (100)",
                        "📊 एल्गोरिदम स्कोर": f"{res['score']} pts"
                    })
                    wa_msg_lines.append(f"• *{col}* (Last: {res['last_num']}) ➔ Single: *{res['single_direct']}* (100)")

            if single_results:
                st.dataframe(pd.DataFrame(single_results), use_container_width=True, hide_index=True)
                
                st.markdown("### 📋 सभी गेम का 1-1 सिंगल नंबर (Copy / Direct Line)")
                direct_line_text = ", ".join([f"{r['👑 1 सिंगल नंबर (No Palat)'].split()[1]}" for r in single_results])
                st.code(direct_line_text, language="text")

                wa_text = "🎯 *TODAY SINGLE DIRECT NUMBERS (NO PALAT)* 🎯\n\n" + "\n".join(wa_msg_lines)
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

            # --- सिंगल नंबर का ऑटोमैटिक पास्ट बैक-टेस्टिंग ---
            st.markdown("---")
            st.subheader("📈 सिंगल नंबर इंजन ऑटोमैटिक पास्ट बैक-टेस्टिंग (Date-wise Pass/Fail)")
            st.write("यहाँ ऐप खुद पीछे के दिनों के लिए सिंगल नंबर का प्रेडिक्शन निकालकर चेक कर रहा है कि वह पास हुआ या फेल:")
            
            sel_game_s = st.selectbox("गेम चुनें (सिंगल पासिंग देखने के लिए):", available_cols, key="backtest_s")
            
            if sel_game_s:
                dates_list_s = df[date_col].tolist() if date_col and date_col in df.columns else [f"Row {i+1}" for i in range(len(df))]
                backtest_data_s = []
                
                for i in range(10, len(df)):
                    sub_df = df.iloc[:i]
                    res_past_s = get_best_single_direct_number(sub_df, sel_game_s)
                    
                    if res_past_s:
                        try:
                            actual_val = int(df.loc[i, sel_game_s])
                            if 0 <= actual_val <= 99:
                                act_str = f"{actual_val:02d}"
                                pred_str = res_past_s["single_direct"]
                                
                                single_pass = "✅ PASS" if pred_str == act_str else "❌ FAIL"
                                row_date = dates_list_s[i] if i < len(dates_list_s) else f"Row {i+1}"
                                
                                backtest_data_s.append({
                                    "📅 दिनांक (Date)": row_date,
                                    "लोकेशन": sel_game_s,
                                    "प्रेडिक्टेड सिंगल नंबर": pred_str,
                                    "वास्तविक रिज़ल्ट": act_str,
                                    "पासिंग स्टेटस": single_pass
                                })
                        except:
                            continue
                
                if backtest_data_s:
                    st.dataframe(pd.DataFrame(backtest_data_s[::-1]), use_container_width=True, hide_index=True)
                else:
                    st.warning("बैकटेस्ट के लिए पर्याप्त डेटा उपलब्ध नहीं है।")

    else:
        st.error("CSV फ़ाइल में DB, SG, FRBD, GZBD, GALI, DSWR में से कोई भी कॉलम नहीं मिला!")
else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर दी गई जगह पर अपनी CSV फ़ाइल अपलोड करें।")
                            
