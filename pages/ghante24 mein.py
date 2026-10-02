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
        "🌐 All-Games Search (24 Hours Pattern)", 
        "🎯 Same-Game Search (उसी गेम में 1-2 दिन का पैटर्न)"
    ])

    # ====================================================
    # TAB 1: ALL GAMES PATTERN
    # ====================================================
    with tab1:
        st.subheader("🌐 किसी भी नंबर के बाद अगले 24 घंटे का ऑल-गेम पैटर्न")
        
        col_a1, col_a2 = st.columns([2, 1])
        with col_a1:
            search_num_all = st.number_input("नंबर दर्ज करें (0 से 99):", min_value=0, max_value=99, value=25, step=1, key="all_num")
        with col_a2:
            btn_all = st.button("🔥 ऑल-गेम सर्च करें", key="btn_all")

        if btn_all or search_num_all is not None:
            next_24h_nums = []
            next_24h_fams = []
            haruf_scores_all = {d: 0 for d in range(10)}
            total_occ_all = 0

            for i in range(len(df) - 1):
                # केवल 0 से 99 तक के वैध अंकों को लेना
                row_vals = [int(x) for x in df.loc[i, available_cols].dropna().tolist() if 0 <= int(x) <= 99]
                if search_num_all in row_vals:
                    total_occ_all += 1
                    for c in available_cols:
                        val_next = df.loc[i + 1, c]
                        if pd.notna(val_next):
                            try:
                                v_int = int(val_next)
                                if 0 <= v_int <= 99:
                                    next_24h_nums.append(v_int)
                                    in_h = v_int // 10
                                    out_h = v_int % 10
                                    
                                    # KeyError रोधक कोड
                                    haruf_scores_all[in_h] = haruf_scores_all.get(in_h, 0) + 1
                                    haruf_scores_all[out_h] = haruf_scores_all.get(out_h, 0) + 1
                                    
                                    rep = get_family_rep(v_int)
                                    if rep is not None:
                                        next_24h_fams.append(rep)
                            except:
                                continue

            if total_occ_all > 0 and len(next_24h_nums) > 0:
                top_2_nums_a = pd.Series(next_24h_nums).value_counts().head(2)
                top_1_fam_a = pd.Series(next_24h_fams).value_counts().head(1)

                num1_a = f"{top_2_nums_a.index[0]:02d}" if len(top_2_nums_a) > 0 else "N/A"
                cnt1_a = top_2_nums_a.iloc[0] if len(top_2_nums_a) > 0 else 0
                num2_a = f"{top_2_nums_a.index[1]:02d}" if len(top_2_nums_a) > 1 else "N/A"
                cnt2_a = top_2_nums_a.iloc[1] if len(top_2_nums_a) > 1 else 0

                top_fam_a = top_1_fam_a.index[0] if len(top_1_fam_a) > 0 else None
                fam_cnt_a = top_1_fam_a.iloc[0] if len(top_1_fam_a) > 0 else 0
                fam_members_a = ", ".join(get_family_members(top_fam_a))

                ranked_h_a = sorted(haruf_scores_all.keys(), key=lambda x: haruf_scores_all[x], reverse=True)

                st.markdown(f"### 📊 ऑल-गेम रिपोर्ट: नंबर `{search_num_all:02d}` (कुल फ्रीक्वेंसी: {total_occ_all} बार)")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("👑 पहला सिंगल नंबर", f"{num1_a}", f"{cnt1_a} बार")
                c2.metric("🥈 दूसरा सिंगल नंबर", f"{num2_a}", f"{cnt2_a} बार")
                c3.metric("🔥 100% पासिंग फैमिली", f"फैमिली {top_fam_a:02d}" if top_fam_a is not None else "N/A", f"{fam_cnt_a} बार")

                st.success(f"📌 **फैमिली {top_fam_a:02d} के पूरे 8 नंबर:** `{fam_members_a}`")

                st.markdown("#### ⚡ 4-हरूफ़ व 6-हरूफ़ ऑल-गेम क्रॉसिंग")
                st.code(f"4 Haruf: [ {', '.join(map(str, sorted(ranked_h_a[:4])))} ]\n6 Haruf: [ {', '.join(map(str, sorted(ranked_h_a[:6])))} ]", language="text")

                # WhatsApp Share Link
                wa_text = (
                    f"🎯 *24 HOUR PATTERN REPORT ({search_num_all:02d})* 🎯\n\n"
                    f"• कुल उपस्थिति: {total_occ_all} बार\n"
                    f"• 👑 1st Single: *{num1_a}* ({cnt1_a} बार)\n"
                    f"• 🥈 2nd Single: *{num2_a}* ({cnt2_a} बार)\n"
                    f"• 🔥 Top Family: *{top_fam_a:02d}* [{fam_members_a}]\n"
                    f"⚡ 4 Haruf: [{', '.join(map(str, sorted(ranked_h_a[:4])))}]\n"
                    f"🔥 6 Haruf: [{', '.join(map(str, sorted(ranked_h_a[:6])))}]"
                )
                encoded_wa = urllib.parse.quote(wa_text)
                wa_url = f"https://api.whatsapp.com/send?text={encoded_wa}"

                st.markdown(
                    f'<a href="{wa_url}" target="_blank">'
                    f'<button style="background-color:#25D366; color:white; border:none; padding:12px 24px; '
                    f'font-size:16px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%;">'
                    f'📲 रिपोर्ट WhatsApp पर शेयर करें'
                    f'</button></a>',
                    unsafe_allow_html=True
                )
            else:
                st.warning(f"13 साल के रिकॉर्ड में नंबर {search_num_all:02d} नहीं मिला।")

    # ====================================================
    # TAB 2: SAME-GAME DIRECT PATTERN (उसी गेम में 1-2 दिन)
    # ====================================================
    with tab2:
        st.subheader("🎯 उसी गेम (Same-Game) में नंबर के बाद 1 से 2 दिन का पैटर्न")
        
        col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
        with col_s1:
            same_num = st.number_input("नंबर डालें (जैसे: 25):", min_value=0, max_value=99, value=25, step=1, key="same_num")
        with col_s2:
            same_game = st.selectbox("गेम सेलेक्ट करें (जैसे: DB / Delhi Bazar):", available_cols, key="same_game")
        with col_s3:
            btn_same = st.button("🔥 उसी गेम में सर्च करें", key="btn_same")

        if btn_same or same_num is not None:
            raw_vals = df[same_game].dropna().tolist()
            game_vals = []
            for x in raw_vals:
                try:
                    v = int(x)
                    if 0 <= v <= 99:
                        game_vals.append(v)
                except:
                    continue
            
            next_2days_nums = []
            next_2days_fams = []
            same_haruf_scores = {d: 0 for d in range(10)}
            total_occ_same = 0

            # उसी गेम में सर्च करना (अगले 1 और 2 दिन)
            for i in range(len(game_vals) - 2):
                if game_vals[i] == same_num:
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
                fam_cnt_s = top_1_fam_s.iloc[0] if len(top_1_fam_s) > 0 else 0
                fam_members_s = ", ".join(get_family_members(top_fam_s))

                ranked_h_s = sorted(same_haruf_scores.keys(), key=lambda x: same_haruf_scores[x], reverse=True)
                top_2_harufs_s = f"{ranked_h_s[0]} और {ranked_h_s[1]}"

                st.markdown(f"### 🎯 `{same_game}` में नंबर `{same_num:02d}` के बाद का 2-दिवसीय पैटर्न:")
                st.info(f"यह नंबर `{same_game}` में पिछले 13 सालों में कुल **{total_occ_same} बार** आया है।")

                sc1, sc2, sc3 = st.columns(3)
                sc1.metric("👑 1st Single Number", f"{num1_s}", f"{cnt1_s} बार गिरा")
                sc2.metric("🥈 2nd Single Number", f"{num2_s}", f"{cnt2_s} बार गिरा")
                sc3.metric("🔥 100% पासिंग फैमिली", f"फैमिली {top_fam_s:02d}" if top_fam_s is not None else "N/A", f"{fam_cnt_s} बार आई")

                st.success(f"📌 **`{same_game}` में फैमिली {top_fam_s:02d} के 8 नंबर:** `{fam_members_s}`")

                st.markdown("---")
                st.subheader(f"⚡ `{same_game}` में अगले 2 दिन के सबसे मजबूत हरूफ़ (Haruf)")

                hc1, hc2 = st.columns(2)
                with hc1:
                    st.metric("👑 टॉप 2 मेन हरूफ़ (अंदर/बाहर)", f"{top_2_harufs_s}")
                with hc2:
                    st.code(f"4 Haruf Crossing: [ {', '.join(map(str, sorted(ranked_h_s[:4])))} ]\n6 Haruf Crossing: [ {', '.join(map(str, sorted(ranked_h_s[:6])))} ]", language="text")

                # WhatsApp Share Button
                wa_same_text = (
                    f"🎯 *SAME-GAME PATTERN REPORT ({same_game})* 🎯\n\n"
                    f"• {same_game} में नंबर {same_num:02d} आने के बाद (अगले 2 दिन):\n"
                    f"• 👑 1st Single: *{num1_s}* ({cnt1_s} बार)\n"
                    f"• 🥈 2nd Single: *{num2_s}* ({cnt2_s} बार)\n"
                    f"• 🔥 Top Family: *{top_fam_s:02d}* [{fam_members_s}]\n"
                    f"• ⚡ Top Harufs (2 Days): *{top_2_harufs_s}*"
                )
                encoded_wa_s = urllib.parse.quote(wa_same_text)
                wa_url_s = f"https://api.whatsapp.com/send?text={encoded_wa_s}"

                st.markdown(
                    f'<a href="{wa_url_s}" target="_blank">'
                    f'<button style="background-color:#25D366; color:white; border:none; padding:12px 24px; '
                    f'font-size:16px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%;">'
                    f'📲 रिपोर्ट WhatsApp पर शेयर करें'
                    f'</button></a>',
                    unsafe_allow_html=True
                )
            else:
                st.warning(f"{same_game} में पिछले 13 सालों में नंबर {same_num:02d} का डेटा नहीं मिला।")

else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर CSV फ़ाइल अपलोड करें।")
                
