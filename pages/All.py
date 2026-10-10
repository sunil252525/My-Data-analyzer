import streamlit as st
import pandas as pd
import urllib.parse

# --- Streamlit Page Config ---
st.set_page_config(page_title="Advanced All-in-One Analytics & 10-Day Backtest Dashboard", layout="wide")

st.title("🎯 All-in-One Game Analytics & 10-Day Backtest Dashboard")
st.write("यहाँ ऊपर आज का मुख्य बॉक्स है और उसके नीचे पिछले 10 दिनों का बिल्कुल वैसा ही पैटर्न वाला पास/फेल रिकॉर्ड दिया गया है।")

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
            "🔥 2. Single Direct Number Engine (10-Day Backtest Boxes)"
        ])
        
        # ==========================================
        # TAB 1: CROSSING ENGINE
        # ==========================================
        with tab1:
            st.subheader("📊 ऐतिहासिक डेटा और फॉलो-अप पैटर्न के आधार पर क्रॉसिंग")
            
            def analyze_best_crossing_and_haruf(df, column_name):
                vals = df[column_name].dropna().tolist()
                valid_vals = []
                for x in vals:
                    try:
                        val = int(float(str(x).strip()))
                        if 0 <= val <= 99:
                            valid_vals.append(val)
                    except:
                        continue
                if len(valid_vals) < 5:
                    return None

                last_num = valid_vals[-1]
                haruf_scores = {d: 0 for d in range(10)}
                
                for idx, num in enumerate(valid_vals):
                    weight = 1 + (idx / len(valid_vals))
                    haruf_scores[num // 10] += weight
                    haruf_scores[num % 10] += weight

                ranked_harufs = sorted(haruf_scores.keys(), key=lambda x: haruf_scores[x], reverse=True)
                
                return {
                    "last_num": f"{last_num:02d}",
                    "single_haruf": str(ranked_harufs[0]),
                    "haruf_4_str": ", ".join(map(str, sorted(ranked_harufs[:4]))),
                    "haruf_6_str": ", ".join(map(str, sorted(ranked_harufs[:6])))
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
                        "🔥 6 हरूफ़ क्रॉसिंग": res["haruf_6_str"]
                    })

            if analysis_results:
                st.dataframe(pd.DataFrame(analysis_results), use_container_width=True, hide_index=True)

        # ==========================================
        # TAB 2: SINGLE DIRECT NUMBER ENGINE (10-DAY BACKTEST)
        # ==========================================
        with tab2:
            st.subheader("🎯 100% सिंगल नंबर डायरेक्ट इंजन (No Palat)")
            
            def get_best_single_direct_number(sub_df, column_name):
                vals = sub_df[column_name].dropna().tolist()
                valid_vals = []
                for x in vals:
                    try:
                        v = int(float(str(x).strip()))
                        if 0 <= v <= 99:
                            valid_vals.append(v)
                    except:
                        continue
                if len(valid_vals) < 5:
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

            # 1. आज का मुख्य टेबल (Present Box) - जैसा स्क्रीनशॉट में है[span_1](start_span)[span_1](end_span)
            single_results = []
            wa_msg_lines = []
            for col in available_cols:
                res = get_best_single_direct_number(df, col)
                if res:
                    single_results.append({
                        "लोकेशन / गेम": col,
                        "🎯 ताज़ा रिज़ल्ट": res["last_num"],
                        "👑 1 सिंगल नंबर (No Palat)": f"🔥 {res['single_direct']} (100)",
                        "📊 एल्गोरिथम स्कोर": f"{res['score']} pts"
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

            # 2. पिछले 10 दिनों के बैक-टेस्टिंग बॉक्सेस (ठीक उसी पैटर्न में)
            st.markdown("---")
            st.subheader("📜 पिछले 10 दिनों का पास्ट रिकॉर्ड (Backtest Boxes)")
            
            dates_list = df[date_col].tolist() if date_col and date_col in df.columns else [f"Day {i+1}" for i in range(len(df))]
            total_rows = len(df)
            box_count = 0
            
            # i = प्रेडिक्शन का दिन, i+1 = अगले दिन का वास्तविक रिजल्ट
            for i in range(total_rows - 2, 0, -1):
                if box_count >= 10:
                    break
                
                sub_df_pred = df.iloc[:i+1]
                pred_date = dates_list[i] if i < len(dates_list) else f"Day {i+1}"
                next_date = dates_list[i+1] if (i+1) < len(dates_list) else f"Day {i+2}"
                
                past_box_rows = []
                
                # अगले दिन (i+1) के वास्तविक रिजल्ट्स
                next_day_results = {}
                for col in available_cols:
                    try:
                        val = int(float(str(df.loc[i+1, col]).strip()))
                        if 0 <= val <= 99:
                            next_day_results[col] = f"{val:02d}"
                    except:
                        pass
                
                # उस दिन (i) के प्रेडिक्टेड सिंगल नंबर
                day_singles = {}
                day_palats = {}
                for col in available_cols:
                    res_s = get_best_single_direct_number(sub_df_pred, col)
                    if res_s:
                        s_num = res_s["single_direct"]
                        day_singles[col] = s_num
                        try:
                            day_palats[col] = f"{int(s_num):02d}"[::-1]
                        except:
                            day_palats[col] = s_num

                for col in available_cols:
                    p_num = day_singles.get(col)
                    p_palat = day_palats.get(col)
                    act_next_val = next_day_results.get(col, "-")
                    
                    # स्कोर या स्टेटस निकालना
                    status_text = "🔴 फेल"
                    if p_num and act_next_val != "-":
                        if p_num == act_next_val:
                            status_text = f"🟢 पास [{act_next_val}] (Same Game)"
                        elif p_palat == act_next_val:
                            status_text = f"🟠 पलट पास [{act_next_val}] (Same Game)"
                        else:
                            other_pass = None
                            for o_col, o_val in next_day_results.items():
                                if o_col != col and (p_num == o_val or p_palat == o_val):
                                    other_pass = o_col
                                    break
                            if other_pass:
                                status_text = f"🟠 अन्य में पास ({other_pass})"

                    past_box_rows.append({
                        "लोकेशन / गेम": col,
                        "🎯 ताज़ा रिज़ल्ट": act_next_val,
                        "👑 1 सिंगल नंबर (No Palat)": f"🔥 {p_num} (100)" if p_num else "-",
                        "📊 एल्गोरिथम स्कोर": status_text
                    })

                if past_box_rows:
                    box_count += 1
                    st.markdown(f"#### 📅 बॉक्स {box_count}: प्रेडिक्शन दिनांक ({pred_date}) ➔ रिज़ल्ट दिनांक ({next_date})")
                    st.dataframe(pd.DataFrame(past_box_rows), use_container_width=True, hide_index=True)
                    st.write("")

    else:
        st.error("CSV फ़ाइल में DB, SG, FRBD, GZBD, GALI, DSWR में से कोई भी कॉलम नहीं मिला!")
else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर दी गई जगह पर अपनी CSV फ़ाइल अपलोड करें।")
            
