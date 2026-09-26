import streamlit as st
import pandas as pd

# ====================================================
# GALI ➔ DSWR MATH & RASHI PATTERN ENGINE (FULLY FIXED)
# ====================================================
RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi_digit(d):
    return RASHI_MAP.get(int(d), int(d))

def run_gali_dswr_custom_pattern(num):
    """
    यूजर का कस्टम घटत (0 -> 10, जोड़ी घटत) और राशि पैटर्न
    """
    try:
        num = int(num)
        d1 = num // 10  # दहाई अंक (Inside)
        d2 = num % 10   # इकाई अंक (Outside)

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

        # 4. हरूफ क्रॉसिंग कॉम्बिनेशन (Pairs)
        pairs = set()
        for h1 in [diff_digit, diff_rashi]:
            for h2 in [d2, d2_rashi]:
                pairs.add(f"{h1}{h2}")
                pairs.add(f"{h2}{h1}")

        return diff_digit, diff_rashi, derived_harufs, sorted(list(pairs))
    except Exception:
        return None, None, [], []

# ----------------------------------------------------
# LIVE ALERT & AUTO SCANNER SECTION
# ----------------------------------------------------
st.markdown("---")
st.subheader("🚨 आज / वर्तमान लाइव पैटर्न अलर्ट (Live Trick Alert)")

# यदि CSV अपलोड हो चुकी है
if 'df' in locals() and df is not None:
    if 'GALI' in df.columns:
        # तारीख कॉलम ऑटो-डिटेक्ट करना
        date_col = 'A' if 'A' in df.columns else df.columns[0]
        
        # केवल सही रिजल्ट वाले रो चुनना
        valid_gali_df = df.dropna(subset=['GALI']).copy()
        
        if not valid_gali_df.empty:
            latest_valid_idx = valid_gali_df.index[-1]
            latest_gali = int(valid_gali_df.loc[latest_valid_idx, 'GALI'])
            latest_date = valid_gali_df.loc[latest_valid_idx, date_col]
            
            # पैटर्न पहचान: अंदर 0 होना (जैसे 07) या जोड़ा होना (जैसे 66)
            d1 = latest_gali // 10
            d2 = latest_gali % 10
            is_special_trick = (d1 == 0) or (d1 == d2)
            
            if is_special_trick:
                st.error(f"🔥 **विशेष ट्रिक अलर्ट:** तारीख `{latest_date}` (GALI: `{latest_gali:02d}`) पर '0/जोड़ा घटत पैटर्न' **एक्टिव (ACTIVE)** है!")
            else:
                st.info(f"📍 **हालिया दर्ज रिजल्ट:** तारीख `{latest_date}` | GALI: `{latest_gali:02d}`")

            # पैटर्न कैलकुलेशन
            diff_d, diff_r, main_harufs, res_pairs = run_gali_dswr_custom_pattern(latest_gali)

            st.write(f"• **गली रिजल्ट:** `{latest_gali:02d}` | **अंतर अंक:** `{diff_d}` (राशि: `{diff_r}`)")

            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                st.markdown("**📋 अगले दिन के लिए मुख्य हरूफ (Direct Copy):**")
                st.code(", ".join(map(str, main_harufs)), language="text")

            with col_g2:
                st.markdown("**🎯 दिसावर/अगले दिन के संभावित नंबर (Direct Copy):**")
                st.code(", ".join(res_pairs), language="text")

            # ----------------------------------------------------
            # HISTORICAL PASSING TRACKER (13 साल की हिस्ट्री पासिंग)
            # ----------------------------------------------------
            st.markdown("---")
            st.subheader("📜 इतिहास में इस ट्रिक की पासिंग लिस्ट (Historical Records)")

            history_data = []
            if 'DSWR' in df.columns:
                for i in range(len(df) - 1):
                    if pd.notna(df.loc[i, 'GALI']) and pd.notna(df.loc[i+1, 'DSWR']):
                        try:
                            g_val = int(df.loc[i, 'GALI'])
                            d_val = int(df.loc[i+1, 'DSWR'])
                            
                            g_d1 = g_val // 10
                            g_d2 = g_val % 10
                            
                            # केवल 0 से शुरू होने वाले (जैसे 07) या जोड़े (जैसे 66) वाले केस
                            if g_d1 == 0 or g_d1 == g_d2:
                                _, _, h_harufs, h_pairs = run_gali_dswr_custom_pattern(g_val)
                                
                                d_str = f"{d_val:02d}"
                                is_hit = (d_str in h_pairs) or (d_val // 10 in h_harufs) or (d_val % 10 in h_harufs)
                                
                                history_data.append({
                                    "तारीख (गली)": df.loc[i, date_col],
                                    "GALI": f"{g_val:02d}",
                                    "निकाले गए हरूफ": ", ".join(map(str, h_harufs)),
                                    "अगली तारीख": df.loc[i+1, date_col],
                                    "DSWR": f"{d_val:02d}",
                                    "ट्रिक पासिंग": "✅ PASS" if is_hit else "❌ FAIL"
                                })
                        except:
                            continue

                if history_data:
                    st.dataframe(pd.DataFrame(history_data), use_container_width=True)
                else:
                    st.write("डेटाबेस में ऐसा कोई ऐतिहासिक पैटर्न रिकॉर्ड नहीं मिला।")
        else:
            st.warning("गली (GALI) कॉलम में डेटा उपलब्ध नहीं है।")
    else:
        st.warning("CSV फ़ाइल में 'GALI' कॉलम नाम नहीं मिला।")
else:
    st.warning("⚠️ कृपया पहले अपनी CSV फ़ाइल अपलोड करें।")
