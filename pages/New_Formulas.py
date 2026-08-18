import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Haruf Rashi Sequence Matcher", layout="wide")

st.title("📊 Haruf & Rashi Pattern Sequence Engine")

uploaded_file = st.file_uploader("अपनी 13 साल की CSV फ़ाइल यहाँ अपलोड करें", type=["csv"], key="dashboard_uploader")

# ================= HELPER FUNCTIONS =================
RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi_digit(d):
    return RASHI_MAP.get(int(d), int(d))

def get_haruf_and_rashi_set(num):
    """एक नंबर के अंदर/बाहर के हरूफ़ और उनकी राशियों का पूरा सेट देता है"""
    try:
        if pd.isna(num): return set()
        num = int(num)
        d1, d2 = num // 10, num % 10
        r1, r2 = get_rashi_digit(d1), get_rashi_digit(d2)
        # मूल हरूफ़ और उनकी राशियाँ
        return {d1, d2, r1, r2}
    except:
        return set()

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    date_col = 'Date' if 'Date' in df.columns else None
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]

    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    df = df.dropna(subset=available_cols, how='all').reset_index(drop=True)

    st.success("✅ 13 साल का डेटाबेस लोड हो गया!")

    st.subheader("🎯 हरूफ़ व राशि लड़ी स्कैनर (Haruf & Rashi Matcher)")
    
    col1, col2 = st.columns(2)
    with col1:
        g_sel = st.selectbox("करंट पैटर्न वाली मुख्य गेम चुनें:", available_cols)
    with col2:
        seq_days = st.slider("लड़ी के दिनों की संख्या (Sequence Length):", 3, 7, 5)

    # हालिया दिनों की लड़ी निकालना
    clean_series = df[g_sel].dropna().astype(int).tolist()
    recent_nums = clean_series[-seq_days:] if len(clean_series) >= seq_days else clean_series

    st.info(f"📌 **`{g_sel}` की हालिया {len(recent_nums)} दिनों की लड़ी:** `{recent_nums}`")

    # हालिया लड़ी के हर दिन के हरूफ़ + राशि सेट बनाना
    recent_haruf_sets = [get_haruf_and_rashi_set(n) for n in recent_nums]

    matched_records = []

    # 13 साल के पूरे डेटाबेस पर 6 गेमों में स्कैन करना
    for col in available_cols:
        col_vals = df[col].tolist()
        for i in range(len(col_vals) - len(recent_nums) - 1):
            sub_seq = col_vals[i : i + len(recent_nums)]
            if any(pd.isna(v) for v in sub_seq):
                continue
            
            sub_seq = [int(v) for v in sub_seq]
            
            # जाँचें कि क्या इतिहास के प्रत्येक दिन का हरूफ़/राशि हालिया लड़ी के हरूफ़/राशि से मेल खाता है
            is_match = True
            for day_idx in range(len(recent_nums)):
                hist_haruf_set = get_haruf_and_rashi_set(sub_seq[day_idx])
                # यदि दोनों दिनों के हरूफ़/राशि सेट में कोई ओवरलैप (साझा अंक) नहीं है, तो मैच नहीं माना जाएगा
                if not (recent_haruf_sets[day_idx] & hist_haruf_set):
                    is_match = False
                    break

            if is_match:
                next_val = col_vals[i + len(recent_nums)]
                if pd.notna(next_val):
                    rec_date = df.loc[i + len(recent_nums), date_col] if date_col else f"Row #{i + len(recent_nums)}"
                    matched_records.append({
                        "तारीख / रो (Date/Row)": rec_date,
                        "गेम का नाम (Game)": col,
                        "ऐतिहासिक लड़ी": str(sub_seq),
                        "अगले दिन आया रिजल्ट (Next Result)": int(next_val)
                    })

    if matched_records:
        res_df = pd.DataFrame(matched_records)
        next_nums = res_df["अगले दिन आया रिजल्ट (Next Result)"].tolist()
        top_5_next = pd.Series(next_nums).value_counts().head(5).to_dict()

        st.success(f"🎯 **13 साल के इतिहास में यह हरूफ़/राशि लड़ी कुल `{len(matched_records)}` बार पाई गई!**")
        st.markdown(f"🔥 **इसके बाद अगले दिन सबसे ज्यादा बार आए अंक (Top 5 Numbers):** `{top_5_next}`")
        st.dataframe(res_df, use_container_width=True)
    else:
        st.warning("⚠️ इस लड़ी के लिए इतिहास में कोई हरूफ़/राशि मैच नहीं मिला। कृपया स्लाइडर से दिनों की संख्या को 3 या 4 करके देखें।")
