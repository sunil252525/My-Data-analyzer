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
st.title("🔬 13-Year Multi-Game Pattern & Crossing Engine")

uploaded_file = st.file_uploader("अपनी CSV फ़ाइल यहाँ अपलोड करें", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    st.success("✅ CSV फ़ाइल सफलतापूर्वक लोड हो गई है!")

    # ----------------------------------------------------
    # TABS STRUCTURE
    # ----------------------------------------------------
    tab1, tab2 = st.tabs([
        "🌐 All-Games Search (00-99 Complete Table)", 
        "🎯 Same-Game Search (1-2 Day Pattern Table)"
    ])

    # ====================================================
    # TAB 1: ALL GAMES PATTERN (00 - 99 SUMMARY TABLE)
    # ====================================================
    with tab1:
        st.subheader("🌐 सभी नंबरों (00 से 99) के बाद अगले 24 घंटे का ऑल-गेम पैटर्न टेबल")
        
        btn_all = st.button("🔥 पूरे 00-99 नंबरों की रिपोर्ट तैयार करें", key="btn_all")

        if btn_all:
            summary_data_all = []

            for search_num in range(100):
                next_24h_nums = []
                next_24h_fams = []
                haruf_scores = {d: 0 for d in range(10)}
                total_occ = 0

                for i in range(len(df) - 1):
                    row_vals = [int(x) for x in df.loc[i, available_cols].dropna().tolist() if 0 <= int(x) <= 99]
                    if search_num in row_vals:
                        total_occ += 1
                        for c in available_cols:
                            val_next = df.loc[i + 1, c]
                            if pd.notna(val_next):
                                try:
                                    v_int = int(val_next)
                                    if 0 <= v_int <= 99:
                                        next_24h_nums.append(v_int)
                                        in_h = v_int // 10
                                        out_h = v_int % 10
                                        
                                        haruf_scores[in_h] = haruf_scores.get(in_h, 0) + 1
                                        haruf_scores[out_h] = haruf_scores.get(out_h, 0) + 1
                                        
                                        rep = get_family_rep(v_int)
                                        if rep is not None:
                                            next_24h_fams.append(rep)
                                except:
                                    continue

                if total_occ > 0 and len(next_24h_nums) > 0:
                    top_2_nums = pd.Series(next_24h_nums).value_counts().head(2)
                    top_1_fam = pd.Series(next_24h_fams).value_counts().head(1)

                    num1 = f"{top_2_nums.index[0]:02d}" if len(top_2_nums) > 0 else "N/A"
                    cnt1 = top_2_nums.iloc[0] if len(top_2_nums) > 0 else 0
                    num2 = f"{top_2_nums.index[1]:02d}" if len(top_2_nums) > 1 else "N/A"
                    cnt2 = top_2_nums.iloc[1] if len(top_2_nums) > 1 else 0

                    top_fam = top_1_fam.index[0] if len(top_1_fam) > 0 else None
                    fam_members = ", ".join(get_family_members(top_fam)) if top_fam is not None else "N/A"

                    ranked_h = sorted(haruf_scores.keys(), key=lambda x: haruf_scores[x], reverse=True)
                    top_haruf = f"{ranked_h[0]}" if len(ranked_h) > 0 else "N/A"

                    summary_data_all.append({
                        "सर्च नंबर": f"{search_num:02d}",
                        "कुल फ्रीक्वेंसी": f"{total_occ} बार",
                        "1st Single": f"{num1} ({cnt1}x)",
                        "2nd Single": f"{num2} ({cnt2}x)",
                        "Top Family": f"फैमिली {top_fam:02d}" if top_fam is not None else "N/A",
                        "फैमिली मेंबर": fam_members,
                        "सिंगल हरूफ़": top_haruf
                    })
                else:
                    summary_data_all.append({
                        "सर्च नंबर": f"{search_num:02d}",
                        "कुल फ्रीक्वेंसी": "0 बार",
                        "1st Single": "N/A",
                        "2nd Single": "N/A",
                        "Top Family": "N/A",
                        "फैमिली मेंबर": "N/A",
                        "सिंगल हरूफ़": "N/A"
                    })

            summary_df_all = pd.DataFrame(summary_data_all)
            st.markdown("### 📊 पूरे 00-99 नंबरों का ऑल-गेम 24H रिपोर्ट टेबल")
            st.dataframe(summary_df_all, height=500, use_container_width=True)

            # WhatsApp Share Format
            wa_lines = ["🌐 *ALL-GAMES 24H PATTERN REPORT (00-99)* 🌐\n"]
            for row in summary_data_all[:10]: # पहली 10 पंक्तियों का उदाहरण (WhatsApp मैसेज लिमिट के अनुसार)
                if row["कुल फ्रीक्वेंसी"] != "0 बार":
                    wa_lines.append(f"• **{row['सर्च नंबर']}** ➔ 1st: *{row['1st Single']}* | 2nd: *{row['2nd Single']}* | Fam: *{row['Top Family']}* | Haruf: *{row['सिंगल हरूफ़']}*")
            
            wa_text_all = "\n".join(wa_lines) + "\n\n*(पूरा टेबल देखने के लिए डैशबोर्ड देखें)*"
            encoded_wa_all = urllib.parse.quote(wa_text_all)
            wa_url_all = f"https://api.whatsapp.com/send?text={encoded_wa_all}"

            st.markdown(
                f'<a href="{wa_url_all}" target="_blank">'
                f'<button style="background-color:#25D366; color:white; border:none; padding:12px 24px; '
                f'font-size:16px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%; margin-top:15px;">'
                f'📲 पूरी रिपोर्ट WhatsApp पर शेयर करें'
                f'</button></a>',
                unsafe_allow_html=True
            )

    # ====================================================
    # TAB 2: SAME-GAME SUMMARY TABLE (00 - 99 PATTERN)
    # ====================================================
    with tab2:
        st.subheader("🎯 उसी गेम (Same-Game) में पूरे 00-99 नंबरों का 1-2 दिन का पैटर्न")
        
        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            same_game = st.selectbox("गेम सेलेक्ट करें:", available_cols, key="same_game")
        with col_s2:
            btn_same = st.button("🔥 गेम रिपोर्ट जनरेट करें", key="btn_same")

        if btn_same:
            raw_vals = df[same_game].dropna().tolist()
            game_vals = []
            for x in raw_vals:
                try:
                    v = int(x)
                    if 0 <= v <= 99:
                        game_vals.append(v)
                except:
                    continue
            
            summary_data_same = []

            for search_num in range(100):
                next_2days_nums = []
                next_2days_fams = []
                same_haruf_scores = {d: 0 for d in range(10)}
                total_occ_same = 0

                for i in range(len(game_vals) - 2):
                    if game_vals[i] == search_num:
                        total_occ_same += 1
                        
                        d1_val = game_vals[i + 1]
                        d2_val = game_vals[i + 2]
                        
                        for v in [d1_val, d2_val]:
                            next_2days_nums.append(v)
                            in_h = v // 10
                            out_h = v % 10
                            same_haruf_scores[in_h] = same_haruf_scores.get(in_h, 0) + 1
                            same_haruf_scores[out_h] = same_haruf_scores.get(out_h, 0) + 1
                            
                            rep = get_family_rep(v)
                            if rep is not None:
                                next_2days_fams.append(rep)

                if total_occ_same > 0 and len(next_2days_nums) > 0:
                    top_2_nums_s = pd.Series(next_2days_nums).value_counts().head(2)
                    top_1_fam_s = pd.Series(next_2days_fams).value_counts().head(1)

                    num1_s = f"{top_2_nums_s.index[0]:02d}" if len(top_2_nums_s) > 0 else "N/A"
                    cnt1_s = top_2_nums_s.iloc[0] if len(top_2_nums_s) > 0 else 0
                    num2_s = f"{top_2_nums_s.index[1]:02d}" if len(top_2_nums_s) > 1 else "N/A"
                    cnt2_s = top_2_nums_s.iloc[1] if len(top_2_nums_s) > 1 else 0

                    top_fam_s = top_1_fam_s.index[0] if len(top_1_fam_s) > 0 else None
                    fam_members_s = ", ".join(get_family_members(top_fam_s)) if top_fam_s is not None else "N/A"

                    ranked_h_s = sorted(same_haruf_scores.keys(), key=lambda x: same_haruf_scores[x], reverse=True)
                    top_haruf_s = f"{ranked_h_s[0]}" if len(ranked_h_s) > 0 else "N/A"

                    summary_data_same.append({
                        "नंबर": f"{search_num:02d}",
                        "कुल उपस्थिति": f"{total_occ_same} बार",
                        "1st Single": f"{num1_s} ({cnt1_s}x)",
                        "2nd Single": f"{num2_s} ({cnt2_s}x)",
                        "Top Family": f"फैमिली {top_fam_s:02d}" if top_fam_s is not None else "N/A",
                        "फैमिली मेंबर": fam_members_s,
                        "सिंगल हरूफ़": top_haruf_s
                    })
                else:
                    summary_data_same.append({
                        "नंबर": f"{search_num:02d}",
                        "कुल उपस्थिति": "0 बार",
                        "1st Single": "N/A",
                        "2nd Single": "N/A",
                        "Top Family": "N/A",
                        "फैमिली मेंबर": "N/A",
                        "सिंगल हरूफ़": "N/A"
                    })

            summary_df_same = pd.DataFrame(summary_data_same)
            st.markdown(f"### 🎯 `{same_game}` गेम - 00 से 99 नंबरों का पैटर्न टेबल")
            st.dataframe(summary_df_same, height=500, use_container_width=True)

            # WhatsApp Share Format
            wa_same_lines = [f"🎯 *SAME-GAME ({same_game}) 1-2 DAY PATTERN* 🎯\n"]
            for row in summary_data_same[:10]:
                if row["कुल उपस्थिति"] != "0 बार":
                    wa_same_lines.append(f"• **{row['नंबर']}** ➔ 1st: *{row['1st Single']}* | 2nd: *{row['2nd Single']}* | Fam: *{row['Top Family']}* | Haruf: *{row['सिंगल हरूफ़']}*")

            wa_same_text = "\n".join(wa_same_lines) + "\n\n*(पूरा टेबल देखने के लिए डैशबोर्ड देखें)*"
            encoded_wa_s = urllib.parse.quote(wa_same_text)
            wa_url_s = f"https://api.whatsapp.com/send?text={encoded_wa_s}"

            st.markdown(
                f'<a href="{wa_url_s}" target="_blank">'
                f'<button style="background-color:#25D366; color:white; border:none; padding:12px 24px; '
                f'font-size:16px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%; margin-top:15px;">'
                f'📲 `{same_game}` रिपोर्ट WhatsApp पर शेयर करें'
                f'</button></a>',
                unsafe_allow_html=True
            )

else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर CSV फ़ाइल अपलोड करें।")
                                  
