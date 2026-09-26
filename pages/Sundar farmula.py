import streamlit as st
import pandas as pd

# ====================================================
# 1. PAGE CONFIGURATION & TITLE
# ====================================================
st.set_page_config(page_title="Multi-Market Pattern Engine", layout="wide")
st.title("🎯 All-Game Pattern & Universal Passing Scanner")

# ====================================================
# 2. FILE UPLOADER SECTION (सबसे ऊपर फ़ाइल अपलोड का बटन)
# ====================================================
uploaded_file = st.file_uploader("📁 अपनी CSV फ़ाइल अपलोड करें", type=["csv"])

# ====================================================
# 3. CUSTOM MATH & RASHI PATTERN ENGINE
# ====================================================
RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi_digit(d):
    return RASHI_MAP.get(int(d), int(d))

def run_custom_math_pattern(num):
    """
    यूजर का कस्टम घटत (0 -> 10, जोड़ी घटत) और राशि पैटर्न
    """
    try:
        num = int(num)
        d1 = num // 10  # दहाई अंक (Inside)
        d2 = num % 10   # इकाई अंक (Outside)

        # घटाव नियम: अंदर 0 होने पर 10 - Outside, नहीं तो |Inside - Outside|
        if d1 == 0:
            diff_val = 10 - d2
        else:
            diff_val = abs(d1 - d2)
        
        diff_digit = diff_val % 10
        diff_rashi = get_rashi_digit(diff_digit)

        # मूल अंकों की राशि
        d2_rashi = get_rashi_digit(d2)

        # मुख्य हरूफ
        derived_harufs = list(dict.fromkeys([diff_digit, diff_rashi, d2, d2_rashi]))

        # हरूफ क्रॉसिंग कॉम्बिनेशन (Pairs)
        pairs = set()
        for h1 in [diff_digit, diff_rashi]:
            for h2 in [d2, d2_rashi]:
                pairs.add(f"{h1}{h2}")
                pairs.add(f"{h2}{h1}")

        return diff_digit, diff_rashi, derived_harufs, sorted(list(pairs))
    except Exception:
        return None, None, [], []

# ====================================================
# 4. DATA LOADING LOGIC (Auto-Load + Manual Upload)
# ====================================================
df = None

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    try:
        df = pd.read_csv("data.csv")
    except Exception:
        df = None

# ====================================================
# 5. ALL GAMES SEPARATE SCANNER (TAB-BY-TAB)
# ====================================================
ALL_MARKETS = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']

if df is not None:
    date_col = 'A' if 'A' in df.columns else df.columns[0]
    available_markets = [m for m in ALL_MARKETS if m in df.columns]

    if available_markets:
        st.markdown("---")
        st.subheader("📌 जिस गेम का पैटर्न देखना चाहते हैं, उसका बटन चुनें:")

        # हर गेम के लिए अलग टैब
        market_tabs = st.tabs([f"🎲 {m}" for m in available_markets])

        for idx, source_m in enumerate(available_markets):
            with market_tabs[idx]:
                st.markdown(f"### 📍 सोर्स मार्केट: **{source_m}**")

                # ----------------------------------------------------
                # A. इस मार्केट का लाइव पैटर्न अलर्ट
                # ----------------------------------------------------
                valid_source_df = df.dropna(subset=[source_m]).copy()

                if not valid_source_df.empty:
                    latest_idx = valid_source_df.index[-1]
                    latest_val = int(valid_source_df.loc[latest_idx, source_m])
                    latest_date = valid_source_df.loc[latest_idx, date_col]

                    d1 = latest_val // 10
                    d2 = latest_val % 10
                    is_special = (d1 == 0) or (d1 == d2)

                    if is_special:
                        st.error(f"🔥 **विशेष ट्रिक अलर्ट:** तारीख `{latest_date}` | `{source_m}`: `{latest_val:02d}` पर '0/जोड़ा घटत पैटर्न' **एक्टिव** है!")
                    else:
                        st.info(f"📍 **हालिया दर्ज रिजल्ट:** तारीख `{latest_date}` | `{source_m}`: `{latest_val:02d}`")

                    diff_d, diff_r, main_harufs, res_pairs = run_custom_math_pattern(latest_val)
                    st.write(f"• **{source_m} रिजल्ट:** `{latest_val:02d}` | **अंतर अंक:** `{diff_d}` (राशि: `{diff_r}`)")

                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**📋 {source_m} से आगे आने वाले गेम्स के लिए मुख्य हरूफ:**")
                        st.code(", ".join(map(str, main_harufs)), language="text")

                    with c2:
                        st.markdown(f"**🎯 {source_m} से आगे आने वाले गेम्स के लिए संभावित नंबर:**")
                        st.code(", ".join(res_pairs), language="text")
                else:
                    st.warning(f"{source_m} में कोई डेटा उपलब्ध नहीं है।")

                # ----------------------------------------------------
                # B. इतिहास में इस मार्केट के पैटर्न की पासिंग रिपोर्ट
                # ----------------------------------------------------
                st.markdown("---")
                st.markdown(f"#### 📜 **{source_m}** में पैटर्न बनने पर बाकी गेम्स में पासिंग का इतिहास")

                history_list = []

                for i in range(len(df)):
                    if pd.notna(df.loc[i, source_m]):
                        try:
                            s_val = int(df.loc[i, source_m])
                            s_d1 = s_val // 10
                            s_d2 = s_val % 10

                            # केवल 0 से शुरू होने वाले (जैसे 07) या जोड़े (जैसे 66)
                            if s_d1 == 0 or s_d1 == s_d2:
                                _, _, h_harufs, h_pairs = run_custom_math_pattern(s_val)

                                passing_details = []
                                steps = 0
                                start_m_idx = available_markets.index(source_m)
                                curr_m_idx = start_m_idx
                                curr_row = i

                                # अगले आने वाले 6 मार्केट्स में पासिंग सर्च करना
                                while steps < 6:
                                    steps += 1
                                    curr_m_idx += 1
                                    if curr_m_idx >= len(available_markets):
                                        curr_m_idx = 0
                                        curr_row += 1

                                    if curr_row < len(df):
                                        t_m = available_markets[curr_m_idx]
                                        t_val = df.loc[curr_row, t_m]

                                        if pd.notna(t_val):
                                            v_t = int(t_val)
                                            t_str = f"{v_t:02d}"
                                            
                                            is_hit = (t_str in h_pairs) or (v_t // 10 in h_harufs) or (v_t % 10 in h_harufs)
                                            if is_hit:
                                                passing_details.append(f"{t_m} ({v_t:02d})")

                                history_list.append({
                                    "तारीख": df.loc[i, date_col],
                                    f"सोर्स ({source_m})": f"{s_val:02d}",
                                    "निकाले गए हरूफ": ", ".join(map(str, h_harufs)),
                                    "संभावित नंबर": ", ".join(h_pairs),
                                    "जिन बाकी गेम्स में पास हुआ": ", ".join(passing_details) if passing_details else "❌ कोई पासिंग नहीं",
                                    "रिजल्ट": f"✅ PASS ({len(passing_details)} गेम)" if passing_details else "❌ FAIL"
                                })
                        except Exception:
                            continue

                if history_list:
                    st.dataframe(pd.DataFrame(history_list), use_container_width=True)
                else:
                    st.write(f"डेटाबेस में {source_m} का ऐसा कोई पैटर्न रिकॉर्ड नहीं मिला।")

    else:
        st.warning("CSV फ़ाइल में कोई भी मान्य गेम कॉलम (DB, SG, FRBD, GZBD, GALI, DSWR) नहीं मिला।")
else:
    st.warning("⚠️ कृपया स्क्रीन पर ऊपर दिए गए बटन से अपनी CSV फ़ाइल अपलोड करें या GitHub रिपॉजिटरी में 'data.csv' नाम से फ़ाइल रखें।")
