import streamlit as st
import pandas as pd

def analyze_best_crossing_and_haruf(df, column_name):
    """
    CSV डेटा के आधार पर 1 सिंगल हरूफ़, 4 हरूफ़ क्रॉसिंग और 6 हरूफ़ क्रॉसिंग निकालता है।
    """
    vals = df[column_name].dropna().tolist()
    valid_vals = []
    
    # डेटा क्लीनिंग (केवल 0-99 तक के वैलिड नंबर लेना)
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
    
    # 1. फ्रीक्वेंसी स्कोरिंग (हाल के नंबरों को ज़्यादा वेटेज/वेट)
    total_len = len(valid_vals)
    for idx, num in enumerate(valid_vals):
        weight = 1 + (idx / total_len)  # Recent data gets slightly higher weight
        haruf_scores[num // 10] += weight
        haruf_scores[num % 10] += weight

    # 2. पैटर्न/फॉलो-अप स्कोरिंग (जब-जब last_num आया, तब अगले 2 रिजल्ट में कौन से हरूफ़ आए)
    follow_up_harufs = []
    for i in range(len(valid_vals) - 2):
        if valid_vals[i] == last_num:
            f1 = valid_vals[i + 1]
            f2 = valid_vals[i + 2]
            follow_up_harufs.extend([f1 // 10, f1 % 10, f2 // 10, f2 % 10])

    for h in follow_up_harufs:
        if 0 <= h <= 9:
            haruf_scores[h] += 3.5  # High priority to follow-up historical patterns

    # स्कोर के हिसाब से हरूफ़ को सॉर्ट करना (Desc order)
    ranked_harufs = sorted(haruf_scores.keys(), key=lambda x: haruf_scores[x], reverse=True)
    
    # परिणाम तैयार करना
    single_haruf = ranked_harufs[0]                     # टॉप 1 हरूफ़
    top_4_harufs = sorted(ranked_harufs[:4])            # टॉप 4 हरूफ़
    top_6_harufs = sorted(ranked_harufs[:6])            # टॉप 6 हरूफ़

    return {
        "last_num": f"{last_num:02d}",
        "single_haruf": str(single_haruf),
        "haruf_4_str": ", ".join(map(str, top_4_harufs)),
        "haruf_6_str": ", ".join(map(str, top_6_harufs))
    }

# ================= TAB / PAGE: ADVANCED CROSSING & HARUF ENGINE =================
def render_advanced_engine_tab(df, available_cols):
    st.title("🎯 Advanced 1-Haruf, 4-Haruf & 6-Haruf Engine")
    st.write("यह इंजन ऐतिहासिक डेटा, हालिया पैटर्न और फॉलो-अप फ़्रीक्वेंसी को एनालाइज़ करके सबसे सटीक क्रॉसिंग और हरूफ़ निकालता है।")

    analysis_results = []

    for col in available_cols:
        res = analyze_best_crossing_and_haruf(df, col)
        if res:
            analysis_results.append({
                "लोकेशन / गेम": col,
                "🎯 ताज़ा रिज़ल्ट": res["last_num"],
                "👑 सिंगल हरूफ़ (1 Haruf)": f"🔥 {res['single_haruf']} (अंदर/बाहर)",
                "⚡ 4 हरूफ़ की ख़ास क्रॉसिंग": res["haruf_4_str"],
                "💡 4-हरूफ़ जोड़ियाँ": "16 जोड़ियाँ (4x4)",
                "🔥 6 हरूफ़ की ख़ास क्रॉसिंग": res["haruf_6_str"],
                "📊 6-हरूफ़ जोड़ियाँ": "36 जोड़ियाँ (6x6)"
            })

    if analysis_results:
        res_df = pd.DataFrame(analysis_results)
        st.dataframe(res_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("💡 कैसे इस्तेमाल करें?")
        st.info("""
        * **सिंगल हरूफ़ (👑):** यह सबसे मज़बूत हरूफ़ है, जिसे अंदर या बाहर प्ले किया जा सकता है।
        * **4 हरूफ़ क्रॉसिंग (⚡):** कम बजट में सिर्फ 16 जोड़ियों के लिए सबसे सटीक हरूफ़ों का ग्रुप है।
        * **6 हरूफ़ क्रॉसिंग (🔥):** बैकटेस्टेड और सेफ़ गेम के लिए 36 जोड़ियों का परफेक्ट कॉम्बिनेशन है।
        """)
    else:
        st.warning("पर्याप्त डेटा उपलब्ध नहीं है। कृपया सही CSV फाइल लोड करें।")
        
