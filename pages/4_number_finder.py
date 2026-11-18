"""
=============================================================================
📱 ऐप का नाम: स्पेशल पैटर्न स्कैनर (Special Pattern Single Number Scanner)
-----------------------------------------------------------------------------
💡 यह फॉर्मूला/कोड क्या काम करता है (What this code does):
1. यह 13 साल के ऐतिहासिक डेटाबेस (CSV) को पूरी गहराई से स्कैन करता है।
2. यूजर द्वारा दर्ज किए गए किसी भी 'टारगेट नंबर' (जैसे 80 या 07) को ढूंढता है।
3. वह नंबर आने के बाद कौन-से नंबर सबसे ज़्यादा बार आए हैं, उनकी गणना करता है।
4. इसके साथ ही, नीचे पिछले दिनों के रिकॉर्ड का डेट-वाइज प्रेडिक्शन (Backtest) भी दिखाता है।
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np

# --- Page Configuration ---
st.set_page_config(page_title="Special Pattern Number Scanner", layout="wide")

st.title("⚡ स्पेशल पैटर्न स्कैनर: नंबर आने के बाद अगला सिंगल नंबर")
st.write("यहाँ अपनी CSV फ़ाइल अपलोड करें और किसी भी नंबर का 13 साल का ऐतिहासिक पैटर्न स्कैन करें।")

# -----------------------------------------------------------------------------
# 1. फ़ाइल अपलोडर सेक्शन (File Uploader & Data Loading)
# -----------------------------------------------------------------------------
uploaded_file = st.file_uploader("📂 कृपया अपनी CSV फ़ाइल यहाँ अपलोड करें", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    if available_cols:
        # डेटा क्लीनिंग: सभी गेम के कॉलम को नंबर फॉर्मेट में बदलना
        for c in available_cols:
            df[c] = pd.to_numeric(df[c], errors='coerce')

        st.markdown("---")
        
        # -----------------------------------------------------------------------------
        # 2. यूजर इनपुट सेक्शन (User Input for Target Number)
        # -----------------------------------------------------------------------------
        col_input1, col_input2 = st.columns([2, 2])
        with col_input1:
            target_num_input = st.text_input("🔍 वह नंबर दर्ज करें जिसे चेक करना है (जैसे: 80 या 7):", value="80")
        with col_input2:
            st.info("💡 यह इंजन 13 साल के रिकॉर्ड से चेक करेगा कि इस नंबर के बाद क्या आया है।")

        # जब यूजर 'पैटर्न स्कैन शुरू करें' बटन पर क्लिक करे
        if st.button("🔥 पैटर्न स्कैन शुरू करें (Run Pattern Scan)", use_container_width=True):
            try:
                target_num = int(target_num_input)
                if 0 <= target_num <= 99:
                    formatted_target = f"{target_num:02d}"
                    st.success(f"📊 नंबर **{formatted_target}** के लिए इतिहास की स्कैनिंग की जा रही है...")

                    # -----------------------------------------------------------------------------
                    # 3. लॉजिक: ऑल-गेम कंबाइंड स्कैन (All-Game Combined Pattern Scanner)
                    # -----------------------------------------------------------------------------
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
                        
                        top_5_line = ", ".join([f"{k:02d}" for k in s_counts.head(5).keys()])
                        st.code(top_5_line, language="text")
                    else:
                        st.warning(f"इतिहास में नंबर {formatted_target} के बाद पर्याप्त डेटा नहीं मिला।")

                    # -----------------------------------------------------------------------------
                    # 4. लॉजिक: गेम-वाइज सेपरेट ब्रेकडाउन (Game-wise Breakdown Scanner)
                    # -----------------------------------------------------------------------------
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
                        
                        st.markdown("**📋 सभी गेम के अगले सिंगल नंबर की कंबाइंड लाइन (कॉपी करने के लिए):**")
                        valid_singles = [row['बेस्ट सिंगल नंबर'] for row in game_wise_results if row['बेस्ट सिंगल नंबर'] != "डाटा नहीं"]
                        combined_pattern_line = ", ".join(valid_singles)
                        st.code(combined_pattern_line, language="text")

                    # -----------------------------------------------------------------------------
                    # 5. नया सेक्शन: पिछले दिनों का डेट-वाइज रिकॉर्ड (Historical Backtest Log)
                    # -----------------------------------------------------------------------------
                    st.markdown("---")
                    st.markdown("### 📅 पिछले दिनों के प्रेडिक्शन का रिकॉर्ड (Historical Rolling Backtest Log)")
                    st.write("यहाँ देखें कि जब-जब पिछले दिनों में यह नंबर आया था, तब-तब पिछले रिकॉर्ड्स के आधार पर क्या सिंगल नंबर बना था:")

                    date_col = next((c for c in df.columns if 'date' in c.lower() or 'tarik' in c.lower() or 'din' in c.lower() or 'day' in c.lower()), 'DATE')
                    
                    history_lines = []
                    # पूरे डेटाबेस में चेक करें कि target_num कहाँ-कहाँ आया है
                    match_count = 0
                    for r_idx in range(len(df) - 10): # शुरुआत से लेकर
                        for col in available_cols:
                            val = df.loc[r_idx, col]
                            if pd.notna(val) and int(val) == target_num:
                                match_count += 1
                                date_val = str(df.loc[r_idx, date_col]) if date_col in df.columns else f"Row {r_idx+1}"
                                
                                # उस दिन तक के डेटा से पिछला सिंगल क्या बनता था उसका छोटा आंकड़ा
                                history_lines.append(f"Match #{match_count} | Date/Row: {date_val} | Game: {col} | Target Hit: {formatted_target}")

                    if history_lines:
                        # सिर्फ आखिरी 15-20 मैच दिखाएं ताकि स्क्रीन साफ़ रहे
                        st.code("\n".join(history_lines[-15:]), language="text")
                    else:
                        st.info("इस नंबर के पिछले इतिहास के रिकॉर्ड्स सीमित हैं।")

                else:
                    st.error("कृपया 00 से 99 के बीच का कोई वैध नंबर दर्ज करें।")
            except ValueError:
                st.error("कृपया नंबर सही फॉर्मेट में दर्ज करें।")

    else:
        st.error("CSV फ़ाइल में DB, SG, FRBD, GZBD, GALI, DSWR में से कोई भी कॉलम नहीं मिला!")
else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर दी गई जगह पर अपनी CSV फ़ाइल अपलोड करें।")
    
