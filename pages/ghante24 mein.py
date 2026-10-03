import streamlit as st
import pandas as pd
import urllib.parse

# Streamlit Page Config
st.set_page_config(page_title="Advanced Pattern & Crossing Search Engine", layout="wide")

# --- RASHI MAP & FAMILY GENERATOR ENGINE ---
RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi_digit(d):
    return RASHI_MAP.get(int(d), int(d))

def get_family_rep(num):
    try:
        num = int(num)
        if not (0 <= num <= 99): return None
        d1, d2 = num // 10, num % 10
        r1, r2 = get_rashi_digit(d1), get_rashi_digit(d2)
        fam = set()
        for a, b in [(d1, d2), (d1, r2), (r1, d2), (r1, r2)]:
            fam.add(a * 10 + b)
            fam.add(b * 10 + a)
        return min(fam)
    except:
        return None

def get_family_members(rep):
    if rep is None: return "N/A"
    d1, d2 = rep // 10, rep % 10
    r1, r2 = get_rashi_digit(d1), get_rashi_digit(d2)
    fam = set()
    for a, b in [(d1, d2), (d1, r2), (r1, d2), (r1, r2)]:
        fam.add(a * 10 + b)
        fam.add(b * 10 + a)
    return sorted([f"{x:02d}" for x in fam])

# --- MAIN DASHBOARD APP ---
st.title("⚡ Multi-Game Auto Pattern Engine")

uploaded_file = st.file_uploader("अपनी CSV फ़ाइल यहाँ अपलोड करें", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip()
        
        series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
        available_cols = [c for c in series_cols if c in df.columns]
        
        if not available_cols:
            st.error("⚠️ CSV फ़ाइल में अपेक्षित कॉलम ('DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR') नहीं मिले।")
        else:
            for c in available_cols:
                df[c] = pd.to_numeric(df[c], errors='coerce')

            st.success("✅ CSV फ़ाइल सफलतापूर्वक लोड हो गई है!")

            tab1, tab2 = st.tabs([
                "🌐 All-Games Search (00-99 Complete 24H Table)", 
                "🎯 Same-Game Search (Last Results Auto Pattern)"
            ])

            # ====================================================
            # TAB 1: ALL GAMES PATTERN
            # ====================================================
            with tab1:
                st.subheader("🌐 पूरे 00 से 99 नंबरों के बाद अगले 24 घंटे का पैटर्न")
                btn_all = st.button("🔥 00 से 99 तक की पूरी रिपोर्ट तैयार करें", key="btn_all")

                if btn_all:
                    summary_data_all = []
                    
                    rows_list = df[available_cols].values.tolist()
                    num_rows = len(rows_list)

                    for search_num in range(100):
                        next_24h_nums = []
                        next_24h_fams = []
                        haruf_scores = [0] * 10
                        total_occ = 0

                        for i in range(num_rows - 1):
                            current_row = [int(x) for x in rows_list[i] if pd.notna(x) and 0 <= int(x) <= 99]
                            if search_num in current_row:
                                total_occ += 1
                                next_row = rows_list[i + 1]
                                for val_next in next_row:
                                    if pd.notna(val_next):
                                        try:
                                            v_int = int(val_next)
                                            if 0 <= v_int <= 99:
                                                next_24h_nums.append(v_int)
                                                haruf_scores[v_int // 10] += 1
                                                haruf_scores[v_int % 10] += 1
                                                rep = get_family_rep(v_int)
                                                if rep is not None:
                                                    next_24h_fams.append(rep)
                                        except:
                                            continue

                        if total_occ > 0 and len(next_24h_nums) > 0:
                            top_3_nums = pd.Series(next_24h_nums).value_counts().head(3)
                            top_1_fam = pd.Series(next_24h_fams).value_counts().head(1)

                            num1 = f"{top_3_nums.index[0]:02d} ({top_3_nums.iloc[0]}x)" if len(top_3_nums) > 0 else "N/A"
                            num2 = f"{top_3_nums.index[1]:02d} ({top_3_nums.iloc[1]}x)" if len(top_3_nums) > 1 else "N/A"
                            num3 = f"{top_3_nums.index[2]:02d} ({top_3_nums.iloc[2]}x)" if len(top_3_nums) > 2 else "N/A"

                            top_fam = top_1_fam.index[0] if len(top_1_fam) > 0 else None
                            fam_members = ", ".join(get_family_members(top_fam)) if top_fam is not None else "N/A"
                            max_haruf = max(range(10), key=lambda x: haruf_scores[x])

                            summary_data_all.append({
                                "सर्च नंबर": f"{search_num:02d}",
                                "कुल उपस्थिति": f"{total_occ} बार",
                                "1st Single": num1,
                                "2nd Single": num2,
                                "3rd Single": num3,
                                "Top Family": f"फैमिली {top_fam:02d}" if top_fam is not None else "N/A",
                                "फैमिली मेंबर": fam_members,
                                "सिंगल हरूफ़": f"{max_haruf}"
                            })
                        else:
                            summary_data_all.append({
                                "सर्च नंबर": f"{search_num:02d}",
                                "कुल उपस्थिति": "0 बार",
                                "1st Single": "N/A",
                                "2nd Single": "N/A",
                                "3rd Single": "N/A",
                                "Top Family": "N/A",
                                "फैमिली मेंबर": "N/A",
                                "सिंगल हरूफ़": "N/A"
                            })

                    summary_df_all = pd.DataFrame(summary_data_all)
                    st.markdown("### 📊 पूरे 00-99 नंबरों का 24H रिपोर्ट टेबल")
                    st.dataframe(summary_df_all, height=500, use_container_width=True)

                    # --- पूरे 100 नंबरों का व्हाट्सएप टेक्स्ट बनाना ---
                    wa_full_lines = ["🌐 *ALL-GAMES COMPLETE PATTERN REPORT (00-99)* 🌐\n"]
                    for row in summary_data_all:
                        if row["कुल उपस्थिति"] != "0 बार":
                            wa_full_lines.append(
                                f"• *{row['सर्च नंबर']}* ({row['कुल उपस्थिति']}) ➔ "
                                f"1st: *{row['1st Single']}* | 2nd: *{row['2nd Single']}* | 3rd: *{row['3rd Single']}* | "
                                f"Fam: *{row['Top Family']}* | Haruf: *{row['सिंगल हरूफ़']}*"
                            )
                    
                    full_report_txt = "\n".join(wa_full_lines)

                    st.markdown("---")
                    st.subheader("📲 पूरे 00 से 99 तक की रिपोर्ट शेयर करने के विकल्प:")

                    col_share1, col_share2 = st.columns(2)

                    with col_share1:
                        # विकल्प 1: सीधे टेक्स्ट डाउनलोड करें
                        st.download_button(
                            label="📥 पूरे 100 नंबरों की रिपोर्ट Text फ़ाइल में डाउनलोड करें",
                            data=full_report_txt,
                            file_name="All_Games_00_99_Report.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

                    with col_share2:
                        # विकल्प 2: पहला आधा भाग (00-49) सीधे WhatsApp पर भेजें
                        wa_text_part1 = "\n".join(wa_full_lines[:50])
                        encoded_wa_part1 = urllib.parse.quote(wa_text_part1)
                        wa_url_part1 = f"https://api.whatsapp.com/send?text={encoded_wa_part1}"
                        
                        st.markdown(
                            f'<a href="{wa_url_part1}" target="_blank">'
                            f'<button style="background-color:#25D366; color:white; border:none; padding:10px 16px; '
                            f'font-size:15px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%;">'
                            f'📲 WhatsApp Direct Share (Part 1)'
                            f'</button></a>',
                            unsafe_allow_html=True
                        )

                    # विकल्प 3: कॉपी-पेस्ट करने के लिए पूरा टेक्स्ट बॉक्स
                    st.markdown("📋 **पूरे 00 से 99 तक के मैसेज को एक क्लिक में कॉपी (Copy) करके WhatsApp पर पेस्ट करें:**")
                    st.code(full_report_txt, language="markdown")

            # ====================================================
            # TAB 2: SAME-GAME SEARCH
            # ====================================================
            with tab2:
                st.subheader("🎯 गेम के ऑटोमैटिक लास्ट रिजल्ट्स पर आधारित पैटर्न")
                col_s1, col_s2 = st.columns([3, 1])
                with col_s1:
                    same_game = st.selectbox("गेम सेलेक्ट करें:", available_cols, key="same_game")
                with col_s2:
                    num_last_results = st.number_input("लास्ट कितने रिजल्ट्स चेक करें?", min_value=1, max_value=20, value=5)

                btn_same = st.button("🔥 ऑटो लास्ट रिजल्ट्स रिपोर्ट जनरेट करें", key="btn_same")

                if btn_same:
                    raw_vals = df[same_game].dropna().tolist()
                    game_vals = [int(x) for x in raw_vals if 0 <= int(x) <= 99]
                    
                    if len(game_vals) >= num_last_results:
                        recent_targets = game_vals[-num_last_results:]
                        st.info(f"📍 `{same_game}` के हालिया {num_last_results} रिजल्ट्स: **{', '.join([f'{x:02d}' for x in recent_targets])}**")
                        
                        summary_data_same = []
                        for target_num in recent_targets:
                            next_2days_nums = []
                            next_2days_fams = []
                            same_haruf_scores = [0] * 10
                            total_occ_same = 0

                            for i in range(len(game_vals) - 2):
                                if game_vals[i] == target_num:
                                    total_occ_same += 1
                                    for v in [game_vals[i + 1], game_vals[i + 2]]:
                                        next_2days_nums.append(v)
                                        same_haruf_scores[v // 10] += 1
                                        same_haruf_scores[v % 10] += 1
                                        rep = get_family_rep(v)
                                        if rep is not None:
                                            next_2days_fams.append(rep)

                            if total_occ_same > 0 and len(next_2days_nums) > 0:
                                top_3_nums_s = pd.Series(next_2days_nums).value_counts().head(3)
                                top_1_fam_s = pd.Series(next_2days_fams).value_counts().head(1)

                                num1_s = f"{top_3_nums_s.index[0]:02d} ({top_3_nums_s.iloc[0]}x)" if len(top_3_nums_s) > 0 else "N/A"
                                num2_s = f"{top_3_nums_s.index[1]:02d} ({top_3_nums_s.iloc[1]}x)" if len(top_3_nums_s) > 1 else "N/A"
                                num3_s = f"{top_3_nums_s.index[2]:02d} ({top_3_nums_s.iloc[2]}x)" if len(top_3_nums_s) > 2 else "N/A"

                                top_fam_s = top_1_fam_s.index[0] if len(top_1_fam_s) > 0 else None
                                fam_members_s = ", ".join(get_family_members(top_fam_s)) if top_fam_s is not None else "N/A"
                                max_haruf_s = max(range(10), key=lambda x: same_haruf_scores[x])

                                summary_data_same.append({
                                    "लास्ट रिजल्ट": f"{target_num:02d}",
                                    "इतिहास में कुल बार": f"{total_occ_same} बार",
                                    "1st Single": num1_s,
                                    "2nd Single": num2_s,
                                    "3rd Single": num3_s,
                                    "Top Family": f"फैमिली {top_fam_s:02d}" if top_fam_s is not None else "N/A",
                                    "फैमिली मेंबर": fam_members_s,
                                    "सिंगल हरूफ़": f"{max_haruf_s}"
                                })

                        summary_df_same = pd.DataFrame(summary_data_same)
                        st.markdown(f"### 🎯 `{same_game}` - हालिया रिजल्ट्स का पैटर्न")
                        st.dataframe(summary_df_same, height=400, use_container_width=True)

                        # WhatsApp Share
                        wa_same_lines = [f"🎯 *SAME-GAME ({same_game}) AUTO LAST RESULTS PATTERN* 🎯\n"]
                        for row in summary_data_same:
                            wa_same_lines.append(
                                f"• **लास्ट नंबर {row['लास्ट रिजल्ट']}** (इतिहास: {row['इतिहास में कुल बार']})\n"
                                f"  ➔ 1st: *{row['1st Single']}* | 2nd: *{row['2nd Single']}* | 3rd: *{row['3rd Single']}*\n"
                                f"  ➔ {row['Top Family']} ({row['फैमिली मेंबर']}) | Haruf: *{row['सिंगल हरूफ़']}*\n"
                            )

                        wa_same_text = "\n".join(wa_same_lines)
                        encoded_wa_s = urllib.parse.quote(wa_same_text)
                        wa_url_s = f"https://api.whatsapp.com/send?text={encoded_wa_s}"

                        st.markdown(
                            f'<a href="{wa_url_s}" target="_blank">'
                            f'<button style="background-color:#25D366; color:white; border:none; padding:12px 24px; '
                            f'font-size:16px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%; margin-top:15px;">'
                            f'📲 `{same_game}` की ऑटो रिपोर्ट WhatsApp पर भेजें'
                            f'</button></a>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.warning("चयनित गेम में पर्याप्त डेटा नहीं है।")

    except Exception as e:
        st.error(f"❌ फ़ाइल पढ़ने में त्रुटि हुई: {e}")

else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर CSV फ़ाइल अपलोड करें।")
