import streamlit as st
import pandas as pd
import urllib.parse

# --- Streamlit Page Config ---
st.set_page_config(page_title="Advanced All-in-One Analytics & Backtesting Engine", layout="wide")

st.title("🎯 All-in-One Game Analytics & Per-Day Tracker")
st.write("यहाँ मुख्य टेबल और उसके नीचे पिछले दिनों का बिल्कुल सटीक डे-बाय-डे पास/फेल रिकॉर्ड दिया गया है।")

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
        tab1, tab2 = st.tabs([
            "🎯 1. Crossing Engine", 
            "🔥 2. Single Direct Number Engine (Color Tracker)"
        ])
        
        # ==========================================
        # TAB 1: CROSSING ENGINE
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
                if len(valid_vals) < 2:
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

            if analysis_results:
                st.dataframe(pd.DataFrame(analysis_results), use_container_width=True, hide_index=True)

        # ==========================================
        # TAB 2: SINGLE DIRECT NUMBER ENGINE (COLOR TRACKER)
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
                if len(valid_vals) < 2:
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
                    "single_direct": f"{best_single_num:02d}"
                }

            single_results = []
            wa_msg_lines = []
            for col in available_cols:
                res = get_best_single_direct_number(df, col)
                if res:
                    single_results.append({
                        "लोकेशन / गेम": col,
                        "🎯 ताज़ा रिज़ल्ट": res["last_num"],
                        "👑 1 सिंगल नंबर (No Palat)": f"🔥 {res['single_direct']}"
                    })
                    wa_msg_lines.append(f"• *{col}* (Last: {res['last_num']}) ➔ Single: *{res['single_direct']}*")

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

            # --- पिछले दिनों का पास/फेल रिकॉर्ड बॉक्स (ऑटो-कैलकुलेटेड) ---
            st.markdown("---")
            st.subheader("📈 पिछले दिनों का सिंगल नंबर पास/फेल रिकॉर्ड (कलर-कोडेड बॉक्स)")
            st.markdown("""
            * **🟢 ग्रीन (Green):** उसी गेम में सेम नंबर पास हुआ।
            * **🟠 ऑरेंज (Orange):** नंबर (या उसकी पलट) किसी दूसरी गेम में पास हुआ।
            * **🔴 रेड (Red):** गेम पूरी तरह फेल रही।
            """)
            
            dates_list_s = df[date_col].tolist() if date_col and date_col in df.columns else [f"Row {i+1}" for i in range(len(df))]
            color_box_data = []
            
            # CSV के डेटा से पिछले 5 से 10 दिनों का रिकॉर्ड अपने आप तैयार करना
            start_idx_s = max(1, len(df) - 10)
            for i in range(len(df) - 1, start_idx_s - 1, -1):
                if i < 1: continue
                sub_df = df.iloc[:i]
                row_date = dates_list_s[i] if i < len(dates_list_s) else f"Row {i+1}"
                
                row_dict = {"📅 दिनांक (Date)": row_date}
                
                day_singles = {}
                day_palats = {}
                for col in available_cols:
                    res_s = get_best_single_direct_number(sub_df, col)
                    if res_s:
                        s_num = res_s["single_direct"]
                        day_singles[col] = s_num
                        try:
                            day_palats[col] = f"{int(s_num):02d}"[::-1]
                        except:
                            day_palats[col] = s_num
                
                actual_results = {}
                for col in available_cols:
                    try:
                        val = int(df.loc[i, col])
                        if 0 <= val <= 99:
                            actual_results[col] = f"{val:02d}"
                    except:
                        pass
                
                has_data = False
                for col in available_cols:
                    p_num = day_singles.get(col)
                    p_palat = day_palats.get(col)
                    act_val = actual_results.get(col)
                    
                    if p_num and act_val:
                        if p_num == act_val:
                            row_dict[col] = f"🟢 पास [{p_num}]"
                            has_data = True
                        elif p_palat == act_val:
                            row_dict[col] = f"🟠 पलट पास [{p_palat}]"
                            has_data = True
                        else:
                            other_hit = None
                            for other_c, other_a in actual_results.items():
                                if other_c != col and (p_num == other_a or p_palat == other_a):
                                    other_hit = other_c
                                    break
                            if other_hit:
                                row_dict[col] = f"🟠 अन्य में ({other_hit})"
                                has_data = True
                            else:
                                row_dict[col] = "🔴 फेल"
                                has_data = True
                    else:
                        row_dict[col] = "-"
                
                if has_data:
                    color_box_data.append(row_dict)
            
            if color_box_data:
                st.dataframe(pd.DataFrame(color_box_data), use_container_width=True, hide_index=True)
            else:
                st.warning("डेटा प्रोसेस करने के लिए पर्याप्त रिकॉर्ड नहीं है।")

    else:
        st.error("CSV फ़ाइल में DB, SG, FRBD, GZBD, GALI, DSWR में से कोई भी कॉलम नहीं मिला!")
else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर दी गई जगह पर अपनी CSV फ़ाइल अपलोड करें।")
                            
