import streamlit as st
import pandas as pd

# ====================================================
# 1. PAGE CONFIGURATION & TITLE
# ====================================================
st.set_page_config(page_title="Universal Pattern Engine", layout="wide")
st.title("🎯 Universal Multi-Market Trick & Passing Scanner")

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
# 5. ALL GAMES SCANNER & HISTORICAL TRACER
# ====================================================
ALL_MARKETS = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']

if df is not None:
    date_col = 'A' if 'A' in df.columns else df.columns[0]
    available_markets = [m for m in ALL_MARKETS if m in df.columns]

    if available_markets:
        # ------------------------------------------------
        # A. ताज़ा पैटर्न अलर्ट (Recent Active Pattern)
        # ------------------------------------------------
        st.markdown("---")
        st.subheader("🚨 ताज़ा लाइव पैटर्न अलर्ट (Recent Trick Alerts)")

        found_active = False
        # हालिया रिकॉर्ड्स में चेक करना (आखिरी 2-3 रो)
        for row_idx in range(len(df)-1, max(-1, len(df)-3), -1):
            r_date = df.loc[row_idx, date_col]
            for m in reversed(available_markets):
                if pd.notna(df.loc[row_idx, m]):
                    try:
                        val = int(df.loc[row_idx, m])
                        d1 = val // 10
                        d2 = val % 10
                        if d1 == 0 or d1 == d2:
                            diff_d, diff_r, main_harufs, res_pairs = run_custom_math_pattern(val)
                            st.error(f"🔥 **पैटर्न अलर्ट:** तारीख `{r_date}` | गेम: **{m}** = `{val:02d}` पर '0/जोड़ा घटत पैटर्न' एक्टिव है!")
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                st.markdown(f"**📋 {m} से अगले आने वाले गेम्स के लिए मुख्य हरूफ:**")
                                st.code(", ".join(map(str, main_harufs)), language="text")
                            with c2:
                                st.markdown(f"**🎯 {m} से अगले आने वाले गेम्स के लिए संभावित नंबर:**")
                                st.code(", ".join(res_pairs), language="text")
                            
                            found_active = True
                            break
                    except Exception:
                        continue
            if found_active:
                break

        if not found_active:
            st.info("📍 हालिया दर्ज रिजल्ट्स में कोई नया '0/जोड़ा घटत पैटर्न' एक्टिव नहीं है।")

        # ------------------------------------------------
        # B. सर्व-गेम पासिंग लिस्ट (Universal Passing Report)
        # ------------------------------------------------
        st.markdown("---")
        st.subheader("📜 इतिहास में किस-किस गेम में यह ट्रिक पास हुई (Universal Passing Tracker)")

        history_records = []

        for i in range(len(df)):
            for j in range(len(available_markets)):
                m_curr = available_markets[j]
                val_curr = df.loc[i, m_curr]

                if pd.notna(val_curr):
                    try:
                        v_c = int(val_curr)
                        c_d1 = v_c // 10
                        c_d2 = v_c % 10

                        # केवल 0 से शुरू होने वाले (जैसे 07) या जोड़े (जैसे 66)
                        if c_d1 == 0 or c_d1 == c_d2:
                            _, _, h_harufs, h_pairs = run_custom_math_pattern(v_c)
                            
                            passing_games = []

                            # इसके बाद आने वाले अगले 6 गेम्स (मार्केट्स) में चेक करना
                            steps = 0
                            curr_idx_m = j
                            curr_idx_row = i

                            while steps < 6:
                                steps += 1
                                curr_idx_m += 1
                                if curr_idx_m >= len(available_markets):
                                    curr_idx_m = 0
                                    curr_idx_row += 1

                                if curr_idx_row < len(df):
                                    target_m = available_markets[curr_idx_m]
                                    target_val = df.loc[curr_idx_row, target_m]

                                    if pd.notna(target_val):
                                        v_t = int(target_val)
                                        t_str = f"{v_t:02d}"
                                        
                                        # हरूफ या जोड़ी मैचिंग
                                        is_hit = (t_str in h_pairs) or (v_t // 10 in h_harufs) or (v_t % 10 in h_harufs)
                                        if is_hit:
                                            passing_games.append(f"{target_m} ({v_t:02d})")

                            history_records.append({
                                "तारीख": df.loc[i, date_col],
                                "जहाँ पैटर्न बना (गेम)": f"{m_curr} ({v_c:02d})",
                                "निकाले गए हरूफ": ", ".join(map(str, h_harufs)),
                                "जिन गेम्स में पास हुआ": ", ".join(passing_games) if passing_games else "❌ कोई पासिंग नहीं",
                                "कुल पासिंग": f"✅ {len(passing_games)} गेम में पास" if passing_games else "❌ FAIL"
                            })
                    except Exception:
                        continue

        if history_records:
            st.dataframe(pd.DataFrame(history_records), use_container_width=True)
        else:
            st.write("डेटाबेस में ऐसा कोई रिकॉर्ड नहीं मिला।")

    else:
        st.warning("CSV फ़ाइल में कोई भी मान्य गेम कॉलम (DB, SG, FRBD, GZBD, GALI, DSWR) नहीं मिला।")
else:
    st.warning("⚠️ कृपया स्क्रीन पर ऊपर दिए गए बटन से अपनी CSV फ़ाइल अपलोड करें या GitHub में 'data.csv' अपलोड करें।")
