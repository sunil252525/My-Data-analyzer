import streamlit as st
import pandas as pd
import numpy as np

# --- Page Configuration ---
st.set_page_config(page_title="Special Pattern Number Scanner", layout="wide")

st.title("⚡ स्पेशल पैटर्न स्कैनर: नंबर आने के बाद अगला सिंगल नंबर (सुधरा हुआ संस्करण)")
st.write("यहाँ अपनी CSV फ़ाइल अपलोड करें और किसी भी नंबर का 13 साल का ऐतिहासिक पैटर्न बिल्कुल सटीक रूप से स्कैन करें।")

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("📂 कृपया अपनी CSV फ़ाइल यहाँ अपलोड करें", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    if available_cols:
        # डेटा क्लीनिंग: सुरक्षित रूप से इंटीजर में बदलना
        for c in available_cols:
            df[c] = pd.to_numeric(df[c], errors='coerce')

        st.markdown("---")
        
        # यूजर इनपुट सेक्शन
        col_input1, col_input2 = st.columns([2, 2])
        with col_input1:
            target_num_input = st.text_input("🔍 वह नंबर दर्ज करें जिसे चेक करना है (जैसे: 80 या 7):", value="80")
        with col_input2:
            st.info("💡 यह सुधरा हुआ इंजन सही क्रम (Sequence) में चेक करेगा कि इस नंबर के ठीक बाद क्या आया है।")

        if st.button("🔥 पैटर्न स्कैन शुरू करें (Run Pattern Scan)", use_container_width=True):
            try:
                target_num = int(target_num_input)
                if 0 <= target_num <= 99:
                    formatted_target = f"{target_num:02d}"
                    st.success(f"📊 नंबर **{formatted_target}** के लिए शुद्ध ऐतिहासिक स्कैनिंग की जा रही है...")

                    # 1. Game-wise Breakdown Scan (सुधारा गया सटीक लॉजिक)
                    st.markdown(f"### 📋 गेम-वाइज सेपरेट ब्रेकडाउन ({formatted_target} आने के ठीक बाद हर गेम का अगला फिक्स नंबर):")
                    
                    game_wise_results = []
                    for col in available_cols:
                        game_next_nums = []
                        # सुधारा गया लूप: केवल ठीक अगले रिकॉर्ड (r_idx + 1) को चेक करेगा
                        for r_idx in range(len(df) - 1):
                            val = df.loc[r_idx, col]
                            if pd.notna(val) and int(val) == target_num:
                                # ठीक अगले दिन/टर्न का नंबर लें
                                nx_val = df.loc[r_idx + 1, col]
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
                                "कुल मैच": f"{len(game_next_nums)} बार",
                                "टॉप 3 संभावित नंबर": top_3_str
                            })
                        else:
                            game_wise_results.append({
                                "लोकेशन / गेम": col,
                                "बेस्ट सिंगल नंबर": "डाटा नहीं",
                                "फ्रीक्वेंसी": "-",
                                "कुल मैच": "0 बार",
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
    
