import streamlit as st
import pandas as pd
import urllib.parse

# --- Streamlit Page Config ---
st.set_page_config(page_title="Advanced All-in-One Analytics & Backtesting Engine", layout="wide")

st.title("🎯 All-in-One Game Analytics & Per-Day Backtesting Engine")
st.write("यहाँ पर-डे (Per-Day) के हिसाब से बिल्कुल सटीक पास/फेल रिकॉर्ड दिखाया गया है जो केवल उसी दिन तक के डेटा पर आधारित है।")

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
            "🎯 1. Crossing Engine (Per-Day Backtest)", 
            "🔥 2. Single Direct Number Engine (Per-Day Palat Tracker)"
        ])
        
        # ==========================================
        # TAB 1: CROSSING ENGINE PER-DAY BACKTEST
        # ==========================================
        with tab1:
            st.subheader("📊 क्रॉसिंग इंजन - पर-डे (Per-Day) सटीक पास/फेल रिकॉर्ड")
            
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

            # आज का ताज़ा एनालिसिस
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

            # --- पर-डे बैक-टेस्टिंग टेबल ---
            st.markdown("---")
            st.subheader("📈 पर-डे (Per-Day) क्रॉसिंग पासिंग रिकॉर्ड")
            sel_game_c = st.selectbox("गेम चुनें:", available_cols, key="perday_c")
            
            if sel_game_c:
                dates_list = df[date_col].tolist() if date_col and date_col in df.columns else [f"Row {i+1}" for i in range(len(df))]
                perday_data_c = []
                
                for i in range(10, len(df)):
                    sub_df = df.iloc[:i] # ठीक उस दिन से पहले का डेटा
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
                                
                                single_pass = "✅ PASS" if (single_h == act_in or single_h == act_out) else "❌ FAIL"
                                h4_pass = "✅ PASS" if (act_in in top4 or act_out in top4) else "❌ FAIL"
                                h6_pass = "✅ PASS" if (act_in in top6 or act_out in top6) else "❌ FAIL"
                                row_date = dates_list[i] if i < len(dates_list) else f"Row {i+1}"
                                
                                perday_data_c.append({
                                    "📅 दिनांक (Date)": row_date,
                                    "लोकेशन": sel_game_c,
                                    "उस दिन का रिजल्ट": act_str,
                                    "सिंगल हरूफ़": res_past["single_haruf"],
                                    "सिंगल स्टेटस": single_pass,
                                    "4 हरूफ़ पासिंग": h4_pass,
                                    "6 हरूफ़ पासिंग": h6_pass
                                })
                        except:
                            continue
                
                if perday_data_c:
                    st.dataframe(pd.DataFrame(perday_data_c[::-1]), use_container_width=True, hide_index=True)
                else:
                    st.warning("पर्याप्त डेटा उपलब्ध नहीं है।")

        # ==========================================
        # TAB 2: SINGLE DIRECT NUMBER ENGINE PER-DAY
        # ==========================================
        with tab2:
            st.subheader("🎯 सिंगल नंबर इंजन - पर-डे (Per-Day) पलट सहित पासिंग रिकॉर्ड")
            
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

            # --- पर-डे पलट पासिंग रिकॉर्ड ---
            st.markdown("---")
            st.subheader("📈 पर-डे (Per-Day) सिंगल नंबर पलट सहित पासिंग रिकॉर्ड")
            st.write("यहाँ हर दिन के अंत में यह चेक किया जा रहा है कि उस दिन के निकाले गए सिंगल नंबरों (पलट सहित) में से कौन सा नंबर किसी भी गेम में पास हुआ:")
            
            dates_list_s = df[date_col].tolist() if date_col and date_col in df.columns else [f"Row {i+1}" for i in range(len(df))]
            perday_data_s = []
            
            for i in range(10, len(df)):
                sub_df = df.iloc[:i] # ठीक उस दिन तक का डेटा
                row_date = dates_list_s[i] if i < len(dates_list_s) else f"Row {i+1}"
                
                # उस दिन के लिए सभी गेम्स के प्रेडिक्टेड सिंगल और उनकी पलट
                predicted_singles = {}
                palat_singles = {}
                for col in available_cols:
                    res_s = get_best_single_direct_number(sub_df, col)
                    if res_s:
                        s_num = res_s["single_direct"]
                        predicted_singles[col] = s_num
                        try:
                            palat_singles[col] = f"{int(s_num):02d}"[::-1]
                        except:
                            palat_singles[col] = s_num
                
                # उस दिन के वास्तविक रिजल्ट्स सभी गेम्स के
                actual_results = {}
                for col in available_cols:
                    try:
                        val = int(df.loc[i, col])
                        if 0 <= val <= 99:
                            actual_results[col] = f"{val:02d}"
                    except:
                        pass
                
                matched_details = []
                hit_found = False
                for game_name, p_num in predicted_singles.items():
                    p_palat = palat_singles[game_name]
                    for act_game, act_val in actual_results.items():
                        if p_num == act_val or p_palat == act_val:
                            hit_found = True
                            matched_details.append(f"{game_name}➔{act_game}({act_val})")
                
                status_str = f"✅ PASS ({', '.join(set(matched_details))})" if hit_found else "❌ FAIL"
                
                row_data = {"📅 दिनांक (Date)": row_date}
                for col in available_cols:
                    pred_p = f"{predicted_singles.get(col, '-')}(प:{palat_singles.get(col, '-')})"
                    act_r = actual_results.get(col, '-')
                    row_data[col] = f"Pred:{pred_p} | Act:{act_r}"
                row_data["पासिंग स्टेटस"] = status_str
                perday_data_s.append(row_data)
            
            if perday_data_s:
                st.dataframe(pd.DataFrame(perday_data_s[::-1]), use_container_width=True, hide_index=True)
            else:
                st.warning("पर्याप्त डेटा उपलब्ध नहीं है।")

    else:
        st.error("CSV फ़ाइल में DB, SG, FRBD, GZBD, GALI, DSWR में से कोई भी कॉलम नहीं मिला!")
else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर दी गई जगह पर अपनी CSV फ़ाइल अपलोड करें।")
                
