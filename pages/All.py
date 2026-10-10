import streamlit as st
import pandas as pd
import urllib.parse

# --- Streamlit Page Config ---
st.set_page_config(page_title="Advanced All-in-One Analytics & Backtesting Engine", layout="wide")

st.title("🎯 All-in-One Game Analytics, Single Number & Backtesting Engine")
st.write("यहाँ आपको **क्रॉसिंग / हरूफ़ एनालिसिस**, **सिंगल डायरेक्ट नंबर इंजन**, और **पिछले रिकॉर्ड की पासिंग (Inside/Outside)** एक ही जगह मिलेगी।")

# --- FILE UPLOADER (SHARED FOR BOTH ENGINES) ---
uploaded_file = st.file_uploader("📂 कृपया अपनी CSV फ़ाइल यहाँ अपलोड करें", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    # यदि CSV में 'Date' या 'Unnamed: 0' जैसी कोई कॉलम है, तो उसे संभालना
    df.columns = df.columns.str.strip()
    
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    if available_cols:
        # Create Tabs for Clean Navigation
        tab1, tab2, tab3 = st.tabs([
            "🎯 Complete Crossing Engine", 
            "🔥 Single Direct Number (No Palat)", 
            "📊 पास्ट रिकॉर्ड & हरूफ़ पासिंग (Back-testing)"
        ])
        
        # ==========================================
        # TAB 1: COMPLETE ANALYTICS & CROSSING ENGINE
        # ==========================================
        with tab1:
            st.subheader("📊 ऐतिहासिक डेटा और फॉलो-अप पैटर्न एनालिसिस")
            
            def analyze_best_crossing_and_haruf(df, column_name):
                vals = df[column_name].dropna().tolist()
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
                    "haruf_6_str": ", ".join(map(str, top_6_harufs))
                }

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
                st.subheader("📲 WhatsApp पर पूरा समरी बॉक्स भेजें")
                
                full_whatsapp_text = "📊 *COMPLETE DAILY ANALYTICS REPORT* 📊\n\n" + "\n\n---\n\n".join(full_box_messages)
                encoded_full_msg = urllib.parse.quote(full_whatsapp_text)
                wa_full_url = f"https://api.whatsapp.com/send?text={encoded_full_msg}"
                
                st.markdown(
                    f'<a href="{wa_full_url}" target="_blank">'
                    f'<button style="background-color:#25D366; color:white; border:none; padding:12px 20px; '
                    f'font-size:16px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%;">'
                    f'📲 पूरा समरी बॉक्स WhatsApp पर भेजें (Crossing & Haruf)'
                    f'</button></a>',
                    unsafe_allow_html=True
                )
        
        # ==========================================
        # TAB 2: SINGLE DIRECT NUMBER ENGINE
        # ==========================================
        with tab2:
            st.subheader("🎯 100% सिंगल नंबर डायरेक्ट इंजन (No Palat)")
            
            def get_best_single_direct_number(df, column_name):
                vals = df[column_name].dropna().tolist()
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
                    "score": round(num_scores[best_single_num], 1)
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

        # ==========================================
        # TAB 3: PAST RECORD & HARUF PASSING (BACK-TESTING)
        # ==========================================
        with tab3:
            st.subheader("📊 पिछले रिकॉर्ड की पासिंग और अंदर-बाहर (Inside/Outside) एनालिसिस")
            st.write("यहाँ पिछले दिनों के रिज़ल्ट, हरूफ़ पासिंग (अंदर या बाहर), और पिछले दिन के मुकाबले आज की पासिंग की पूरी टेबल दी गई है:")

            # गेम चुनने के लिए ड्रॉपडाउन
            selected_game_for_history = st.selectbox("गेम चुनें:", available_cols)
            
            if selected_game_for_history:
                raw_series = df[selected_game_for_history].dropna().tolist()
                
                # यदि CSV में कोई 'Date' या 'Unnamed: 0' नाम का कॉलम है, तो उसे डेट के रूप में उपयोग करें
                date_col = None
                for c in df.columns:
                    if 'date' in c.lower() or 'din' in c.lower() or 'दिनांक' in c:
                        date_col = c
                        break
                
                dates_list = df[date_col].tolist() if date_col else [f"Day {i+1}" for i in range(len(df))]

                history_data = []
                for i in range(1, len(raw_series)):
                    try:
                        curr_val = int(raw_series[i])
                        prev_val = int(raw_series[i-1])
                        
                        if 0 <= curr_val <= 99 and 0 <= prev_val <= 99:
                            c_str = f"{curr_val:02d}"
                            p_str = f"{prev_val:02d}"
                            
                            in_digit = c_str[0]
                            out_digit = c_str[1]
                            
                            # यह चेक करने के लिए कि पिछले दिन के रिज़ल्ट का हरूफ़ आज अंदर या बाहर आया या नहीं
                            prev_in = p_str[0]
                            prev_out = p_str[1]
                            
                            matched_type = []
                            if prev_in == in_digit or prev_out == in_digit:
                                matched_type.append("अंदर (Inside)")
                            if prev_in == out_digit or prev_out == out_digit:
                                matched_type.append("बाहर (Outside)")
                                
                            status_str = ", ".join(matched_type) if matched_type else "Miss"
                            
                            history_data.append({
                                "तारीख / दिन": dates_list[i] if i < len(dates_list) else f"Row {i}",
                                "पिछला रिज़ल्ट (कल)": p_str,
                                "नया रिज़ल्ट (आज)": c_str,
                                "अंदर अंक": in_digit,
                                "बाहर अंक": out_digit,
                                "पासिंग स्टेटस (Inside/Outside)": status_str
                            })
                    except:
                        continue
                
                if history_data:
                    history_df = pd.DataFrame(history_data[::-1]) # नवीनतम रिकॉर्ड ऊपर दिखाने के लिए उलट दें
                    st.dataframe(history_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("इस गेम के लिए पर्याप्त पास्ट रिकॉर्ड डेटा उपलब्ध नहीं है।")

    else:
        st.error("CSV फ़ाइल में DB, SG, FRBD, GZBD, GALI, DSWR में से कोई भी कॉलम नहीं मिला!")
else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर दी गई जगह पर अपनी CSV फ़ाइल अपलोड करें।")
                
