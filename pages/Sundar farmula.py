import streamlit as st
import pandas as pd

# ----------------------------------------------------
# 1. RASHI & CUSTOM MATH ENGINE
# ----------------------------------------------------
RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi_digit(d):
    return RASHI_MAP.get(int(d), int(d))

def run_gali_dswr_custom_pattern(num):
    """
    यूजर का कस्टम घटत (0 -> 10, जोड़ी घटत) और राशि पैटर्न
    """
    try:
        num = int(num)
        d1 = num // 10  # दहाई (Inside)
        d2 = num % 10   # इकाई (Outside)

        # 1. घटाव नियम: अंदर 0 होने पर 10 - Outside, नहीं तो |Inside - Outside|
        if d1 == 0:
            diff_val = 10 - d2
        else:
            diff_val = abs(d1 - d2)
        
        diff_digit = diff_val % 10
        diff_rashi = get_rashi_digit(diff_digit)

        # 2. मूल अंकों की राशि
        d2_rashi = get_rashi_digit(d2)

        # 3. मुख्य हरूफ
        derived_harufs = list(dict.fromkeys([diff_digit, diff_rashi, d2, d2_rashi]))

        # 4. हरूफ क्रॉसिंग कॉम्बिनेशन
        pairs = set()
        for h1 in [diff_digit, diff_rashi]:
            for h2 in [d2, d2_rashi]:
                pairs.add(f"{h1}{h2}")
                pairs.add(f"{h2}{h1}")

        return diff_digit, diff_rashi, derived_harufs, sorted(list(pairs))
    except:
        return None, None, [], []

# ----------------------------------------------------
# 2. PRESENT LIVE ALERT & SCANNER ENGINE
# ----------------------------------------------------
st.markdown("---")
st.subheader("🚨 आज/वर्तमान के लाइव पैटर्न अलर्ट (Today's Live Trick Alert)")

# यदि CSV पहले से लोड है
if 'df' in locals() and df is not None and 'GALI' in df.columns:
    
    # 1. सबसे हालिया (Latest/Present) गली रिजल्ट निकालना
    latest_valid_idx = df['GALI'].dropna().index[-1]
    latest_gali = int(df.loc[latest_valid_idx, 'GALI'])
    latest_date = df.loc[latest_valid_idx, 'A'] if 'A' in df.columns else f"Row {latest_valid_idx}"
    
    # 2. चेक करना कि क्या यह वही पैटर्न है (0 से शुरू होने वाला या जोड़ा)
    d1 = latest_gali // 10
    d2 = latest_gali % 10
    
    is_pattern_active = (d1 == 0) or (d1 == d2)
    
    if is_pattern_active:
        st.error(f"🔥 **लाइव अलर्ट:** आज/हालिया रिजल्ट `{latest_date}` (GALI: `{latest_gali:02d}`) पर यह घटाव/राशि ट्रिक **सक्रिय (ACTIVE)** है!")
    else:
        st.info(f"📍 **हालिया रिजल्ट:** `{latest_date}` | GALI: `{latest_gali:02d}` (सामान्य घटत लॉजिक लागू)")

    # 3. पैटर्न कैलकुलेशन
    diff_d, diff_r, main_harufs, res_pairs = run_gali_dswr_custom_pattern(latest_gali)

    st.write(f"• **इनपुट नंबर:** `{latest_gali:02d}` | **गणितीय अंतर:** `{diff_d}` (राशि: `{diff_r}`)")

    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("**📋 अगले दिन के लिए मुख्य हरूफ (Direct Copy):**")
        st.code(", ".join(map(str, main_harufs)), language="text")

    with col_g2:
        st.markdown("**🎯 अगले दिन (दिसावर/Next Day) के संभावित नंबर:**")
        st.code(", ".join(res_pairs), language="text")

    # ----------------------------------------------------
    # 3. HISTORICAL PASSING TRACKER (इतिहास में पासिंग रिकॉर्ड)
    # ----------------------------------------------------
    st.markdown("---")
    st.subheader("📜 इतिहास में जहाँ-जहाँ यह ट्रिक बनी और पास हुई")

    history_data = []
    if 'DSWR' in df.columns:
        for i in range(len(df) - 1):
            if pd.notna(df.loc[i, 'GALI']) and pd.notna(df.loc[i+1, 'DSWR']):
                g_val = int(df.loc[i, 'GALI'])
                d_val = int(df.loc[i+1, 'DSWR'])
                
                g_d1 = g_val // 10
                g_d2 = g_val % 10
                
                # केवल 0 या जोड़े वाले पैटर्न या सभी घटत को स्कैन करना
                if g_d1 == 0 or g_d1 == g_d2:
                    _, _, h_harufs, h_pairs = run_gali_dswr_custom_pattern(g_val)
                    
                    d_str = f"{d_val:02d}"
                    is_hit = (d_str in h_pairs) or (d_val // 10 in h_harufs) or (d_val % 10 in h_harufs)
                    
                    history_data.append({
                        "तारीख (गली)": df.loc[i, 'A'] if 'A' in df.columns else f"Row {i}",
                        "GALI Result": f"{g_val:02d}",
                        "निकाले गए हरूफ": str(h_harufs),
                        "अगली तारीख": df.loc[i+1, 'A'] if 'A' in df.columns else f"Row {i+1}",
                        "DSWR Result": f"{d_val:02d}",
                        "ट्रिक स्टेटस": "✅ पास (PASS)" if is_hit else "❌ फेल (FAIL)"
                    })

        if history_data:
            st.dataframe(pd.DataFrame(history_data), use_container_width=True)
else:
    st.warning("कृपया ऐप में ऊपर अपनी CSV फ़ाइल अपलोड करें।")
