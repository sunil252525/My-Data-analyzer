import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse

# Page Layout Configuration
st.set_page_config(page_title="Advanced All-in-One Analytics & Dashboard", layout="wide")

st.title("🎯 All-in-One Game Analytics & Multi-Game Dashboard")
st.write("यहाँ सभी एडवांस इंजन, क्रॉसिंग, सिंगल नंबर और डीप हिस्टोरिकल पैटर्न एक ही डैशबोर्ड में उपलब्ध हैं।")

# --- RASHI & FAMILY GENERATOR ENGINE ---
RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi_digit(d):
    return RASHI_MAP.get(int(d), int(d))

def get_family(num):
    try:
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

def get_haruf(num):
    try:
        num = int(num)
        return num // 10, num % 10
    except:
        return None, None

def get_plat(num_val):
    try:
        num_str = f"{int(num_val):02d}"
        return num_str[::-1]
    except:
        return ""

def fmt_line(num_list, rate):
    clean_nums = []
    for n in num_list:
        try:
            clean_nums.append(f"{int(n):02d}")
        except:
            clean_nums.append(str(n))
    if not clean_nums:
        return ""
    return f"{', '.join(clean_nums)} ({rate})"

# --- FILE UPLOADER (SHARED FOR ALL TABS) ---
uploaded_file = st.file_uploader("📂 कृपया अपनी CSV फ़ाइल यहाँ अपलोड करें", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    
    if available_cols:
        tab1, tab2, tab3 = st.tabs([
            "🎯 1. Complete Crossing & Haruf Engine", 
            "🔥 2. Single Direct Number Engine (No Palat)",
            "🔬 3. Deep Historical Pattern & Analytics"
        ])
        
        # ==========================================
        # TAB 1: COMPLETE CROSSING & HARUF ENGINE
        # ==========================================
        with tab1:
            st.subheader("📊 ऐतिहासिक डेटा और फॉलो-अप पैटर्न के आधार पर क्रॉसिंग")
            
            def analyze_best_crossing_and_haruf(df_sub, column_name):
                vals = df_sub[column_name].dropna().tolist()
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
                    "single_h_int": single_haruf
                }

            analysis_results = []
            full_box_messages = []
            all_unique_harufs = set()

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
                    
                    all_unique_harufs.add(res["single_h_int"])
                    
                    game_msg = (
                        f"🎯 *{col}* (Last: {res['last_num']})\n"
                        f"👑 सिंगल हरूफ़: *{res['single_haruf']}* (अंदर/बाहर)\n"
                        f"⚡ 4 हरूफ़: [{res['haruf_4_str']}]\n"
                        f"🔥 6 हरूफ़: [{res['haruf_6_str']}]"
                    )
                    full_box_messages.append(game_msg)

            if analysis_results:
                st.dataframe(pd.DataFrame(analysis_results), use_container_width=True, hide_index=True)
                
                # सभी सिंगल हरूफ़ की संयुक्त (Unique) क्रॉसिंग
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
        # TAB 2: SINGLE DIRECT NUMBER ENGINE
        # ==========================================
        with tab2:
            st.subheader("🎯 100% सिंगल नंबर डायरेक्ट इंजन (No Palat)")
            
            def get_best_single_direct_number(df_sub, column_name):
                vals = df_sub[column_name].dropna().tolist()
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

        # ==========================================
        # TAB 3: DEEP HISTORICAL PATTERN & ANALYTICS
        # ==========================================
        with tab3:
            st.subheader("🔬 Deep Historical Pattern & Analytics Engine")
            
            run_scan = st.button("🔥 Run Multi-Game Auto Scan (एक साथ सभी गेम देखें)", use_container_width=True)
            
            if run_scan:
                sub_tabs = st.tabs([f"🎯 {col}" for col in available_cols])
                all_games_24h_summary = []
                
                for idx, col in enumerate(available_cols):
                    with sub_tabs[idx]:
                        valid_series = df[col].dropna().astype(int)
                        if valid_series.empty:
                            st.warning(f"{col} में कोई वैध डेटा नहीं है।")
                            continue
                        
                        last_result = valid_series.iloc[-1]
                        t_idx = df[df[col] == last_result].index
                        total_hist_count = len(t_idx)
                        
                        d1_idx = [i + 1 for i in t_idx if i + 1 < len(df)]
                        d2_idx = [i + 2 for i in t_idx if i + 2 < len(df)]
                        
                        d1_vals_list = df.loc[d1_idx, col].dropna().astype(int).tolist()
                        d2_vals_list = df.loc[d2_idx, col].dropna().astype(int).tolist()

                        if total_hist_count == 0:
                            st.warning(f"इतिहास में {col} में नंबर {last_result:02d} दर्ज नहीं है।")
                        else:
                            d1_vals = pd.Series(d1_vals_list)
                            d2_vals = pd.Series(d2_vals_list)
                            
                            opps_d1, opps_d2 = len(d1_vals), len(d2_vals)
                            top_1d = d1_vals.value_counts().head(5)
                            top_2d = d2_vals.value_counts().head(5)
                            
                            target_fam = get_family(last_result)
                            fam_m1 = sum(1 for v in d1_vals_list if v in target_fam)
                            fam_m2 = sum(1 for v in d2_vals_list if v in target_fam)
                            fam_obs_rate = round(((fam_m1 + fam_m2) / (opps_d1 + opps_d2)) * 100, 2) if (opps_d1 + opps_d2) > 0 else 0.0
                            
                            in_h_top2 = d1_vals.apply(lambda x: x // 10).value_counts().head(2)
                            out_h_top2 = d1_vals.apply(lambda x: x % 10).value_counts().head(2)

                            in_harufs = list(in_h_top2.index)[:2]
                            out_harufs = list(out_h_top2.index)[:2]

                            crossed_line1 = [f"{i}{o}" for i in in_harufs for o in out_harufs]
                            crossed_line2 = [f"{o}{i}" for i in in_harufs for o in out_harufs]
                            all_cross_digits = list(dict.fromkeys(in_harufs + out_harufs))
                            total_16_cross = [f"{d1}{d2}" for d1 in all_cross_digits for d2 in all_cross_digits]

                            seen_cross = set()
                            l1_clean, l2_clean = [], []
                            for num in crossed_line1:
                                if num not in seen_cross: l1_clean.append(num); seen_cross.add(num)
                            for num in crossed_line2:
                                if num not in seen_cross: l2_clean.append(num); seen_cross.add(num)
                            l3_clean = [num for num in total_16_cross if num not in seen_cross]
                            pairs_list = [f"{h}{h}" for h in all_cross_digits]

                            next_24h_numbers, haruf_in_24h, haruf_out_24h = [], [], []
                            for match_i in t_idx:
                                if match_i + 1 < len(df):
                                    for c_24 in available_cols:
                                        val_24 = df.loc[match_i + 1, c_24]
                                        if pd.notna(val_24):
                                            val_int = int(val_24)
                                            next_24h_numbers.append(val_int)
                                            h_i, h_o = get_haruf(val_int)
                                            if h_i is not None: haruf_in_24h.append(h_i)
                                            if h_o is not None: haruf_out_24h.append(h_o)

                            top_24h_series = pd.Series(next_24h_numbers).value_counts().head(5) if next_24h_numbers else pd.Series()
                            top_24h_direct = [f"{num:02d}" for num in top_24h_series.index]
                            top_24h_plat = [get_plat(n) for n in top_24h_direct]

                            top_in_24h = pd.Series(haruf_in_24h).value_counts().head(3).index.tolist() if haruf_in_24h else []
                            top_out_24h = pd.Series(haruf_out_24h).value_counts().head(3).index.tolist() if haruf_out_24h else []

                            crossed_24h_direct = [f"{i}{o}" for i in top_in_24h for o in top_out_24h]
                            all_24h_harufs = list(dict.fromkeys(top_in_24h + top_out_24h))
                            haruf_24h_pairs = [f"{h}{h}" for h in all_24h_harufs]

                            seen_haruf_nums = set()
                            h_nums_clean = []
                            for n in crossed_24h_direct:
                                if n not in seen_haruf_nums: h_nums_clean.append(n); seen_haruf_nums.add(n)

                            h_plat_clean = []
                            for n in [get_plat(p) for p in crossed_24h_direct]:
                                if n not in seen_haruf_nums: h_plat_clean.append(n); seen_haruf_nums.add(n)
                            for p in haruf_24h_pairs:
                                if p not in seen_haruf_nums: h_plat_clean.append(p); seen_haruf_nums.add(p)

                            top_1d_direct = [f"{num:02d}" for num in top_1d.index]
                            top_1d_plat = [get_plat(n) for n in top_1d_direct]
                            top_2d_direct = [f"{num:02d}" for num in top_2d.index]
                            top_2d_plat = [get_plat(n) for n in top_2d_direct]

                            # 1. Executive Summary
                            st.subheader(f"📌 {col} का ऐतिहासिक विश्लेषण (Last Result: {last_result:02d})")
                            st.write(f"• **मुख्य ऐतिहासिक निष्कर्ष:** 13 साल के रिकॉर्ड में **{col}** में **{last_result:02d}** कुल **{total_hist_count} बार** आया है।")
                            
                            top_1d_str = ", ".join([f"{k:02d}: {v} बार" for k, v in top_1d.to_dict().items()])
                            top_2d_str = ", ".join([f"{k:02d}: {v} बार" for k, v in top_2d.to_dict().items()])
                            top_24h_str = ", ".join([f"{k:02d}: {v} बार" for k, v in top_24h_series.to_dict().items()])
                            
                            st.write(f"• **सबसे मजबूत 1-Day Follow-up:** {top_1d_str}")
                            st.write(f"• **सबसे मजबूत 2-Day Follow-up:** {top_2d_str}")
                            st.write(f"• **24-Hour All-Games Repeat:** {top_24h_str}")
                            st.write(f"• **फैमिली पासिंग दर:** Observed Rate = **{fam_obs_rate}%**")
                            
                            st.markdown("---")
                            
                            # 2. Individual Boxes
                            st.markdown("### 📋 अलग-अलग कैटेगरी बॉक्स")
                            c_box1, c_box2 = st.columns(2)

                            with c_box1:
                                st.markdown("**🎯 हरूफ़ क्रॉसिंग 16 नंबर (Line 1: 100, Line 2 & 3: 50):**")
                                st.code(f"{fmt_line(l1_clean, 100)}\n{fmt_line(l2_clean, 50)}\n{fmt_line(l3_clean, 50)}", language="text")

                                st.markdown("**📋 1-Day Follow-up Numbers (सीधी + पलट):**")
                                st.code(f"{fmt_line(top_1d_direct, 50)}\n{fmt_line(top_1d_plat, 50)}", language="text")

                                st.markdown("**⚡ 24-Hour All-Games Numbers (24 घंटे सभी गेम रिपीट):**")
                                st.code(f"{fmt_line(top_24h_direct, 100)}\n{fmt_line(top_24h_plat, 50)}", language="text")

                            with c_box2:
                                st.markdown("**👯 हरूफ के जोड़े (Pairs / Jode):**")
                                st.code(fmt_line(pairs_list, 50), language="text")

                                st.markdown("**📋 2-Day Follow-up Numbers (सीधी + पलट):**")
                                st.code(f"{fmt_line(top_2d_direct, 50)}\n{fmt_line(top_2d_plat, 50)}", language="text")

                                st.markdown("**🎲 24-Hour Haruf Numbers & Pairs (सीधी + पलट):**")
                                st.code(f"{fmt_line(h_nums_clean, 50)}\n{fmt_line(h_plat_clean, 50)}", language="text")

                            game_24h_str = (
                                f"🎮 *{col}*⚡\n"
                                f"{fmt_line(top_24h_direct, 100)}\n"
                                f"{fmt_line(top_24h_plat, 50)}\n\n"
                                f"🎲\n"
                                f"{fmt_line(h_nums_clean, 50)}\n"
                                f"{fmt_line(h_plat_clean, 50)}"
                            )
                            all_games_24h_summary.append(game_24h_str)

                if all_games_24h_summary:
                    st.markdown("---")
                    full_whatsapp_msg = "\n\n".join(all_games_24h_summary)
                    encoded_all_msg = urllib.parse.quote(full_whatsapp_msg)
                    all_whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_all_msg}"

                    st.markdown(
                        f'<a href="{all_whatsapp_url}" target="_blank">'
                        f'<button style="background-color:#25D366; color:white; border:none; padding:15px 30px; '
                        f'font-size:18px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%;">'
                        f'📲 सभी गेम्स (ALL GAMES 24H BOXES) को एक साथ WhatsApp पर शेयर करें'
                        f'</button></a>',
                        unsafe_allow_html=True
                    )

    else:
        st.error("CSV फ़ाइल में DB, SG, FRBD, GZBD, GALI, DSWR में से कोई भी कॉलम नहीं मिला!")
else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर दी गई जगह पर अपनी CSV फ़ाइल अपलोड करें।")
                                
