import streamlit as st
import pandas as pd
import urllib.parse

# Streamlit Page Config
st.set_page_config(page_title="24 Ghante Mein - Search Engine", layout="wide")

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
    d1, d2 = rep // 10, rep % 10
    r1, r2 = get_rashi_digit(d1), get_rashi_digit(d2)
    fam = set()
    for a, b in [(d1, d2), (d1, r2), (r1, d2), (r1, r2)]:
        fam.add(a * 10 + b)
        fam.add(b * 10 + a)
    return sorted([f"{x:02d}" for x in fam])

# --- MAIN PAGE APP ---
st.title("🔬 24 घंटे का ऑल-गेम पैटर्न सर्च")

uploaded_file = st.file_uploader("अपनी CSV फ़ाइल यहाँ अपलोड करें", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    st.success("✅ CSV फ़ाइल सफलतापूर्वक लोड हो गई है!")

    st.markdown("---")
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
            row_vals = df.loc[i, available_cols].dropna().astype(int).tolist()
            if search_num_all in row_vals:
                total_occ_all += 1
                for c in available_cols:
                    val_next = df.loc[i + 1, c]
                    if pd.notna(val_next):
                        v_int = int(val_next)
                        # केवल 0 से 99 तक के वैध अंकों को ही स्कोर में जोड़ें
                        if 0 <= v_int <= 99:
                            next_24h_nums.append(v_int)
                            in_h = v_int // 10
                            out_h = v_int % 10
                            
                            # KeyError से बचाने के लिए सुरक्षित जोड़
                            haruf_scores_all[in_h] = haruf_scores_all.get(in_h, 0) + 1
                            haruf_scores_all[out_h] = haruf_scores_all.get(out_h, 0) + 1
                            
                            rep = get_family_rep(v_int)
                            if rep is not None:
                                next_24h_fams.append(rep)

        if total_occ_all > 0:
            top_2_nums_a = pd.Series(next_24h_nums).value_counts().head(2)
            top_1_fam_a = pd.Series(next_24h_fams).value_counts().head(1)

            num1_a = f"{top_2_nums_a.index[0]:02d}" if len(top_2_nums_a) > 0 else "N/A"
            cnt1_a = top_2_nums_a.iloc[0] if len(top_2_nums_a) > 0 else 0
            num2_a = f"{top_2_nums_a.index[1]:02d}" if len(top_2_nums_a) > 1 else "N/A"
            cnt2_a = top_2_nums_a.iloc[1] if len(top_2_nums_a) > 1 else 0

            top_fam_a = top_1_fam_a.index[0] if len(top_1_fam_a) > 0 else None
            fam_cnt_a = top_1_fam_a.iloc[0] if len(top_1_fam_a) > 0 else 0
            fam_members_a = ", ".join(get_family_members(top_fam_a)) if top_fam_a is not None else "N/A"

            ranked_h_a = sorted(haruf_scores_all.keys(), key=lambda x: haruf_scores_all[x], reverse=True)

            st.markdown(f"### 📊 ऑल-गेम रिपोर्ट: नंबर `{search_num_all:02d}` (कुल फ्रीक्वेंसी: {total_occ_all} बार)")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("👑 पहला सिंगल नंबर", f"{num1_a}", f"{cnt1_a} बार")
            c2.metric("🥈 दूसरा सिंगल नंबर", f"{num2_a}", f"{cnt2_a} बार")
            c3.metric("🔥 100% पासिंग फैमिली", f"फैमिली {top_fam_a:02d}", f"{fam_cnt_a} बार")

            st.success(f"📌 **फैमिली {top_fam_a:02d} के पूरे 8 नंबर:** `{fam_members_a}`")

            st.markdown("#### ⚡ 4-हरूफ़ व 6-हरूफ़ ऑल-गेम क्रॉसिंग")
            st.code(f"4 Haruf: [ {', '.join(map(str, sorted(ranked_h_a[:4])))} ]\n6 Haruf: [ {', '.join(map(str, sorted(ranked_h_a[:6])))} ]", language="text")

            # WhatsApp Link
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
            st.warning(f"रिकॉर्ड में नंबर {search_num_all:02d} नहीं मिला।")

else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर CSV फ़ाइल अपलोड करें।")
            
