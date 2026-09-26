import streamlit as st
import pandas as pd
import numpy as np

# Page Layout Configuration
st.set_page_config(page_title="Gali-Dswr Custom Math Pattern Engine", layout="wide")

st.title("🎯 GALI ➔ DSWR घटाव व राशि पैटर्न स्कैनर (Auto-Alert Engine)")
st.write("यह टूल आपके द्वारा बताए गए 'गली के घटाव व राशि' लॉजिक के आधार पर ऐतिहासिक चार्ट को स्कैन करता है और अलर्ट जारी करता है।")

# ----------------------------------------------------
# 1. RASHI & CUSTOM MATH ENGINE
# ----------------------------------------------------
RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi(d):
    return RASHI_MAP.get(int(d), int(d))

def process_gali_math_pattern(num):
    """
    यूजर के घटाव व राशि लॉजिक को प्रोसेस करता है
    """
    try:
        num = int(num)
        d1 = num // 10  # दहाई (Inside)
        d2 = num % 10   # इकाई (Outside)

        # 1. 0/अंक घटाव लॉजिक (Zero & Same Number Rules)
        if d1 == 0:
            diff = 10 - d2
        else:
            diff = abs(d1 - d2)
        
        diff = diff % 10
        diff_r = get_rashi(diff)

        # 2. मूल अंकों की राशि
        d1_r = get_rashi(d1)
        d2_r = get_rashi(d2)

        # 3. मुख्य हरूफ
        harufs = list(dict.fromkeys([diff, diff_r, d2, d2_r]))

        # 4. हरूफ क्रॉसिंग कॉम्बिनेशन
        pairs = set()
        for h1 in [diff, diff_r]:
            for h2 in [d2, d2_r]:
                pairs.add(f"{h1}{h2}")
                pairs.add(f"{h2}{h1}")

        return diff, diff_r, harufs, sorted(list(pairs))
    except:
        return None, None, [], []

# ----------------------------------------------------
# 2. Main Page CSV Uploader
# ----------------------------------------------------
uploaded_file = st.file_uploader("अपनी 13 साल की CSV फ़ाइल अपलोड करें", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Ensure Numeric Conversion
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    st.success("✅ डेटाबेस लोड हो गया!")

    # ----------------------------------------------------
    # 3. Pattern Detection Section
    # ----------------------------------------------------
    st.markdown("---")
    st.subheader("🚨 हालिया / वर्तमान पैटर्न अलर्ट (Live Pattern Detection)")

    if 'GALI' in df.columns and 'DSWR' in df.columns:
        # Get the latest row from dataset
        latest_idx = df['GALI'].dropna().index[-1]
        latest_date = df.loc[latest_idx, 'A'] if 'A' in df.columns else f"Row {latest_idx}"
        latest_gali_res = int(df.loc[latest_idx, 'GALI'])

        diff, diff_r, harufs, pairs = process_gali_math_pattern(latest_gali_res)

        st.info(f"📍 **अंतिम दर्ज रिजल्ट:** तारीख/रो: `{latest_date}` | **गली (GALI):** `{latest_gali_res:02d}`")

        st.markdown(f"### 🔥 अगले दिन (दिसावर/DSWR) के लिए संभावित अलर्ट:")
        st.write(f"• **गली का नंबर:** `{latest_gali_res:02d}`")
        st.write(f"• **गणितीय अंतर अंक (Diff):** `{diff}` (राशि: `{diff_r}`)")

        # Direct Copy Boxes
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**📋 मुख्य निकाले गए हरूफ (Copy Box):**")
            st.code(", ".join(map(str, harufs)), language="text")

        with c2:
            st.markdown("**🎯 दिसावर/अगले दिन के संभावित नंबर (Copy Box):**")
            st.code(", ".join(pairs), language="text")

        # ----------------------------------------------------
        # 4. Historical Pattern Hit Table
        # ----------------------------------------------------
        st.markdown("---")
        st.subheader("📜 इतिहास में जहाँ-जहाँ यह पैटर्न बना (Historical Hits)")

        history_hits = []
        for i in range(len(df) - 1):
            if pd.notna(df.loc[i, 'GALI']) and pd.notna(df.loc[i+1, 'DSWR']):
                g_val = int(df.loc[i, 'GALI'])
                d_val = int(df.loc[i+1, 'DSWR'])
                
                # Check for 0-start (e.g., 07, 02) or Double Digits (e.g., 66)
                g_d1 = g_val // 10
                g_d2 = g_val % 10
                
                if g_d1 == 0 or g_d1 == g_d2:
                    h_diff, h_diff_r, h_harufs, h_pairs = process_gali_math_pattern(g_val)
                    
                    # Target Hits Check
                    d_str = f"{d_val:02d}"
                    is_hit = d_str in h_pairs or (d_val // 10 in h_harufs) or (d_val % 10 in h_harufs)
                    
                    date_val = df.loc[i, 'A'] if 'A' in df.columns else f"Row {i}"
                    next_date_val = df.loc[i+1, 'A'] if 'A' in df.columns else f"Row {i+1}"
                    
                    history_hits.append({
                        "तारीख (गली)": date_val,
                        "GALI Result": f"{g_val:02d}",
                        "निकाले गए हरूफ": str(h_harufs),
                        "अगली तारीख": next_date_val,
                        "DSWR Result": f"{d_val:02d}",
                        "पैटर्न स्टेटस": "✅ HIT/PASS" if is_hit else "❌ FAILED"
                    })

        if history_hits:
            st.dataframe(pd.DataFrame(history_hits), use_container_width=True)
        else:
            st.write("डेटाबेस में कोई मैच नहीं मिला।")
    else:
        st.error("CSV फ़ाइल में 'GALI' और 'DSWR' नाम के कॉलम होने आवश्यक हैं।")
