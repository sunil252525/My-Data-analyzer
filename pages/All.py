import streamlit as st
import pandas as pd
import urllib.parse

# Streamlit Page Config
st.set_page_config(page_title="Advanced All-in-One Engine", layout="wide")

# --- 1. CORE LOGIC FUNCTION ---
def analyze_best_crossing_and_haruf(df, column_name):
    vals = df[column_name].dropna().tolist()
    valid_vals = []
    
    for x in vals:
        try:
            val = int(x)
            if 0 <= val <= 99:
                valid_vals.append(val)
        except:
            continue
            
    if len(valid_vals) < 5:
        return None

    last_num = valid_vals[-1]
    haruf_scores = {d: 0 for d in range(10)}
    
    total_len = len(valid_vals)
    for idx, num in enumerate(valid_vals):
        weight = 1 + (idx / total_len)
        haruf_scores[num // 10] += weight
        haruf_scores[num % 10] += weight

    follow_up_harufs = []
    for i in range(len(valid_vals) - 2):
        if valid_vals[i] == last_num:
            f1 = valid_vals[i + 1]
            f2 = valid_vals[i + 2]
            follow_up_harufs.extend([f1 // 10, f1 % 10, f2 // 10, f2 % 10])

    for h in follow_up_harufs:
        if 0 <= h <= 9:
            haruf_scores[h] += 3.5

    ranked_harufs = sorted(haruf_scores.keys(), key=lambda x: haruf_scores[x], reverse=True)
    
    single_haruf = ranked_harufs[0]
    top_4_harufs = sorted(ranked_harufs[:4])
    top_6_harufs = sorted(ranked_harufs[:6])

    return {
        "last_num": f"{last_num:02d}",
        "single_haruf": str(single_haruf),
        "haruf_4_str": ", ".join(map(str, top_4_harufs)),
        "haruf_6_str": ", ".join(map(str, top_6_harufs))
    }

# --- 2. RENDER ENGINE FUNCTION ---
def render_advanced_engine_tab(df, available_cols):
    st.title("🎯 Complete Analytics & Crossing Engine")
    st.write("ऐतिहासिक डेटा और फॉलो-अप पैटर्न के आधार पर एनालाइज किया गया परिणाम:")

    analysis_results = []
    full_box_messages = []

    for col in available_cols:
        res = analyze_best_crossing_and_haruf(df, col)
        if res:
            analysis_results.append({
                "लोकेशन / गेम": col,
                "🎯 ताज़ा रिज़ल्ट": res["last_num"],
                "👑 सिंगल हरूफ़ (1 Haruf)": f"🔥 {res['single_haruf']} (अंदर/बाहर)",
                "⚡ 4 हरूफ़ क्रॉसिंग": res["haruf_4_str"],
                "💡 4-हरूफ़ जोड़ियाँ": "16 जोड़ियाँ (4x4)",
                "🔥 6 हरूफ़ क्रॉसिंग": res["haruf_6_str"],
                "📊 6-हरूफ़ जोड़ियाँ": "36 जोड़ियाँ (6x6)"
            })
            
            # पूरा बॉक्स मैसेज फ़ॉर्मैट करना
            game_msg = (
                f"🎯 *{col}* (Last: {res['last_num']})\n"
                f"👑 सिंगल हरूफ़: *{res['single_haruf']}* (अंदर/बाहर)\n"
                f"⚡ 4 हरूफ़ (16 जोड़ियाँ): [{res['haruf_4_str']}]\n"
                f"🔥 6 हरूफ़ (36 जोड़ियाँ): [{res['haruf_6_str']}]"
            )
            full_box_messages.append(game_msg)

    if analysis_results:
        res_df = pd.DataFrame(analysis_results)
        st.dataframe(res_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("📲 WhatsApp पर पूरा समरी बॉक्स भेजें")
        
        # --- FULL BOX WHATSAPP SHARE LINK ---
        full_whatsapp_text = "📊 *COMPLETE DAILY ANALYTICS REPORT* 📊\n\n" + "\n\n---\n\n".join(full_box_messages)
        encoded_full_msg = urllib.parse.quote(full_whatsapp_text)
        wa_full_url = f"https://api.whatsapp.com/send?text={encoded_full_msg}"
        
        st.markdown(
            f'<a href="{wa_full_url}" target="_blank">'
            f'<button style="background-color:#25D366; color:white; border:none; padding:15px 25px; '
            f'font-size:18px; border-radius:10px; cursor:pointer; font-weight:bold; width:100%;">'
            f'📲 पूरा समरी बॉक्स WhatsApp पर भेजें (Click to Share Full Box)'
            f'</button></a>',
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.subheader("💡 निर्देश (Instructions):")
        st.info("""
        * **सिंगल हरूफ़ (👑):** सबसे मज़बूत हरूफ़ (अंदर/बाहर के लिए)।
        * **4 हरूफ़ क्रॉसिंग (⚡):** 16 जोड़ियों का कम बजट कॉम्बिनेशन।
        * **6 हरूफ़ क्रॉसिंग (🔥):** 36 जोड़ियों की ऑल-टाइम सेफ़ क्रॉसिंग।
        * **WhatsApp बटन:** बटन दबाते ही सिंगल हरूफ़, 4-हरूफ़ और 6-हरूफ़ तीनों की डिटेल्स एक साथ मैसेज में चली जाएँगी।
        """)
    else:
        st.warning("डेटा कम है या मैचिंग कॉलम नहीं मिले।")

# --- 3. MAIN APP EXECUTION ---
st.title("📂 CSV Data Analyzer Dashboard")
uploaded_file = st.file_uploader("अपनी CSV फ़ाइल यहाँ अपलोड करें", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    if available_cols:
        render_advanced_engine_tab(df, available_cols)
    else:
        st.error("CSV में DB, SG, FRBD, GZBD, GALI, DSWR में से कोई भी कॉलम नहीं मिला।")
else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर CSV फ़ाइल अपलोड करें।")
    
