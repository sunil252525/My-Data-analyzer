import streamlit as st
import pandas as pd
import numpy as np

# --- Page Configuration ---
st.set_page_config(page_title="Special Pattern Single Number Scanner", layout="wide")

st.title("⚡ स्पेशल पैटर्न स्कैनर: नंबर आने के बाद अगला सिंगल नंबर")
st.write("यहाँ अपनी CSV फ़ाइल अपलोड करें और किसी भी नंबर का 13 साल का ऐतिहासिक पैटर्न स्कैन करें।")

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("📂 कृपया अपनी CSV फ़ाइल यहाँ अपलोड करें", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    if available_cols:
        # डेटा क्लीनिंग
        for c in available_cols:
            df[c] = pd.to_numeric(df[c], errors='coerce')

        st.markdown("---")
        
        # यूजर इनपुट सेक्शन
        col_input1, col_input2 = st.columns([2, 2])
        with col_input1:
            target_num_input = st.text_input("🔍 वह नंबर दर्ज करें जिसे चेक करना है (जैसे: 80 या 7):", value="80")
        with col_input2:
            st.info("💡 यह इंजन 13 साल के रिकॉर्ड से चेक करेगा कि इस नंबर के बाद क्या आया है।")

        if st.button("🔥 पैटर्न स्कैन शुरू करें (Run Pattern Scan)", use_container_width=True):
            try:
                target_num = int(target_num_input)
                if 0 <= target_num <= 99:
                    formatted_target = f"{target_num:02d}"
                    st.success(f"📊 नंबर **{formatted_target}** के लिए इतिहास की स्कैनिंग की जा रही है...")

                    # 1. All-Game Combined Scan
                    next_day_all_numbers = []
                    
                    for r_idx in range(len(df) - 1):
                        for c_idx, col in enumerate(available_cols):
                            val = df.loc[r_idx, col]
                            if pd.notna(val) and int(val) == target_num:
                                collected = 0
                                curr_r = r_idx
                                curr_c = c_idx + 1
                                while collected < 6 and curr_r < len(df):
                                    while curr_c < len(available_cols):
                                        next_val = df.loc[curr_r, available_cols[curr_c]]
                                        if pd.notna(next_val):
                                            next_day_all_numbers.append(int(next_val))
                                            collected += 1
                                        curr_c += 1
                                        if collected >= 6: break
                                    curr_r += 1
                                    curr_c = 0

                    if next_day_all_numbers:
                        s_counts = pd.Series(next_day_all_numbers).value_counts()
                        top_single = s_counts.index[0]
                        top_count = s_counts.iloc[0]

                        st.markdown("### 🎯 1. ऑल-गेम कंबाइंड रिजल्ट (सभी मार्केट मिलाकर):")
                        st.info(
                            f"• **सबसे ताकतवर सिंगल नंबर:** **{top_single:02d}** (इतिहास में कुल **{top_count} बार** देखा गया)\n"
                            f"• **टॉप 5 सबसे ज्यादा आने वाले नंबर:** " + ", ".join([f"**{k:02d}** ({v} बार)" for k, v in s_counts.head(5).items()])
                        )
                        
                        # कंबाइंड लाइन जिसे आप एक क्लिक में कॉपी कर सकें
                        top_5_line = ", ".join([f"{k:02d}" for k in s_counts.head(5).keys()])
                        st.code(top_5_line, language="text")
                    else:
                        st.warning(f"इतिहास में नंबर {formatted_target} के बाद पर्याप्त डेटा नहीं मिला।")

                    # 2. Game-wise Breakdown Scan
                    st.markdown("---")
                    st.markdown(f"### 📋 2. गेम-वाइज सेपरेट ब्रेकडाउन ({formatted_target} आने के बाद हर गेम का अगला फिक्स नंबर):")
                    
                    game_wise_results = []
                    for col in available_cols:
                        game_next_nums = []
                        for r_idx in range(len(df) - 1):
                            val = df.loc[r_idx, col]
                            if pd.notna(val) and int(val) == target_num:
                                for skip in range(1, 4):
                                    if r_idx + skip < len(df):
                                        nx_val = df.loc[r_idx + skip, col]
                                        if pd.notna(nx_val):
                                            game_next_nums.append(int(nx_val))
                        
                        if game_next_nums:
                            g_series = pd.Series(game_next_nums).value_counts()
                            best_n = g_series.index[0]
                            best_cnt = g_series.iloc[0]
                            top_3_str = ", ".join([f"{k:02d} ({v} बार)" for k, v in g_series.head(3).items()])
                            game_wise_results.append({
                                "लोकेशन / गेम": col,
                                "बेस्ट सिंगल नंबर": f"{best_n:02d}",
                                "फ्रीक्वेंसी": f"{best_cnt} बार",
                                "टॉप 3 संभावित नंबर": top_3_str
                            })
                        else:
                            game_wise_results.append({
                                "लोकेशन / गेम": col,
                                "बेस्ट सिंगल नंबर": "डाटा नहीं",
                                "फ्रीक्वेंसी": "-",
                                "टॉप 3 संभावित नंबर": "-"
                            })

                    if game_wise_results:
                        res_df_pattern = pd.DataFrame(game_wise_results)
                        st.dataframe(res_df_pattern, use_container_width=True, hide_index=True)
                        
                        # सभी गेम के अगले सिंगल नंबर की एक साथ कंबाइंड लाइन
                        st.markdown("**📋 सभी गेम के अगले सिंगल नंबर की कंबाइंड लाइन (कॉपी करने के लिए):**")
                        valid_singles = [row['बेस्ट सिंगल नंबर'] for row in game_wise_results if row['बेस्ट सिंगल नंबर'] != "डाटा नहीं"]
                        combined_pattern_line = ", ".join(valid_singles)
                        st.code(combined_pattern_line, language="text")

                else:
                    st.error("कृपया 00 से 99 के बीच का कोई वैध नंबर दर्ज करें।")
            except ValueError:
                st.error("कृपया नंबर सही फॉर्मेट में दर्ज करें।")

    else:
        st.error("CSV फ़ाइल में DB, SG, FRBD, GZBD, GALI, DSWR में से कोई भी कॉलम नहीं मिला!")
else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर दी गई जगह पर अपनी CSV फ़ाइल अपलोड करें।")
  
