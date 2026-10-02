import streamlit as st
import pandas as pd
import urllib.parse

# Streamlit Page Config
st.set_page_config(page_title="Number Pattern & Family Search Engine", layout="wide")

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

# --- MAIN DASHBOARD APP ---
st.title("🔬 13-Year Number Pattern & Family Engine")
st.write("किसी भी नंबर के आने पर उसके अगले 24 घंटों का **टॉप 2 सिंगल नंबर** और **सबसे ज़्यादा पास होने वाली 1 फैमिली** निकालें:")

uploaded_file = st.file_uploader("अपनी CSV फ़ाइल अपलोड करें", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    st.success("✅ CSV फ़ाइल सफलतापूर्वक लोड हो गई है!")

    st.markdown("---")
    st.subheader("🔍 नंबर सर्च करें (Search Any Number)")

    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        search_num = st.number_input("नंबर डालें (0 से 99, उदाहरण: 25):", min_value=0, max_value=99, value=25, step=1)
    with col_s2:
        search_btn = st.button("🔥 एनालाइज़ और सर्च करें")

    if search_btn or search_num is not None:
        next_24h_nums = []
        next_24h_fams = []
        total_occurrences = 0

        for i in range(len(df) - 1):
            row_vals = df.loc[i, available_cols].dropna().astype(int).tolist()
            if search_num in row_vals:
                total_occurrences += 1
                for c in available_cols:
                    val_next = df.loc[i + 1, c]
                    if pd.notna(val_next):
                        v_int = int(val_next)
                        next_24h_nums.append(v_int)
                        rep = get_family_rep(v_int)
                        if rep is not None:
                            next_24h_fams.append(rep)

        if total_occurrences > 0:
            top_2_nums = pd.Series(next_24h_nums).value_counts().head(2)
            top_1_fam = pd.Series(next_24h_fams).value_counts().head(1)

            num1 = f"{top_2_nums.index[0]:02d}" if len(top_2_nums) > 0 else "N/A"
            num1_cnt = top_2_nums.iloc[0] if len(top_2_nums) > 0 else 0

            num2 = f"{top_2_nums.index[1]:02d}" if len(top_2_nums) > 1 else "N/A"
            num2_cnt = top_2_nums.iloc[1] if len(top_2_nums) > 1 else 0

            top_fam_rep = top_1_fam.index[0] if len(top_1_fam) > 0 else None
            top_fam_cnt = top_1_fam.iloc[0] if len(top_1_fam) > 0 else 0
            fam_members_str = ", ".join(get_family_members(top_fam_rep)) if top_fam_rep is not None else "N/A"

            st.markdown(f"### 📊 नंबर `{search_num:02d}` का 13 साल का विश्लेषण:")
            st.info(f"यह नंबर पूरे रिकॉर्ड में **{total_occurrences} बार** आया है।")

            col_res1, col_res2, col_res3 = st.columns(3)

            with col_res1:
                st.metric("👑 पहला मुख्य सिंगल नंबर", f"{num1}", f"{num1_cnt} बार आया")

            with col_res2:
                st.metric("🥈 दूसरा मुख्य सिंगल नंबर", f"{num2}", f"{num2_cnt} बार आया")

            with col_res3:
                st.metric("🔥 100% ऑल-टाइम पासिंग फैमिली", f"फैमिली {top_fam_rep:02d}", f"{top_fam_cnt} बार आई")

            st.markdown("---")
            st.success(f"📌 **फैमिली {top_fam_rep:02d} के पूरे 8 नंबर:** `{fam_members_str}`")

            # WhatsApp Share Link
            wa_text = (
                f"🎯 *PATTERN REPORT FOR NUMBER {search_num:02d}* 🎯\n\n"
                f"• कुल उपस्थिति: {total_occurrences} बार\n"
                f"• 👑 पहला सिंगल नंबर: *{num1}* ({num1_cnt} बार)\n"
                f"• 🥈 दूसरा सिंगल नंबर: *{num2}* ({num2_cnt} बार)\n"
                f"• 🔥 नंबर 1 फैमिली: *{top_fam_rep:02d}* [{fam_members_str}] ({top_fam_cnt} बार)"
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
            st.warning(f"13 साल के रिकॉर्ड में नंबर {search_num:02d} नहीं मिला।")

else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर CSV फ़ाइल अपलोड करें।")
    
