"""
=============================================================================
📱 ऐप का नाम: Tabbed Multi-Market Pattern & Master Copy Scanner
-----------------------------------------------------------------------------
💡 मुख्य विशेषताएँ:
- दो अलग-अलग टैब: 
  1. गेम-वाइज सेपरेट ऑटो-स्कैन और मास्टर कंबाइंड बॉक्स
  2. ऑल-गेम क्रॉस-मार्केट कंबाइंड पैटर्न स्कैनर
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np

# --- Page Configuration ---
st.set_page_config(page_title="Multi-Tab Pattern Matcher", layout="wide")

st.title("🎯 एडवांस्ड ऑल-इन-वन पैटर्न और सिंगल स्कैनर")
st.write("यह ऐप टैब के जरिए अलग-अलग और क्रॉस-मार्केट पैटर्न स्कैनिंग की सुविधा देता है।")

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
        
        # --- यहाँ दो स्पष्ट टैब बनाए गए हैं ---
        tab1, tab2 = st.tabs([
            "⚡ 1. हर गेम का अलग-अलग ऑटो-स्कैन और मास्टर बॉक्स", 
            "🔍 2. ऑल-गेम क्रॉस-मार्केट पैटर्न स्कैनर"
        ])
        
        # ==========================================
        # TAB 1: गेम-वाइज सेपरेट ऑटो-स्कैन और मास्टर बॉक्स
        # ==========================================
        with tab1:
            st.subheader("📊 सभी छह मार्केट के अलग-अलग ऑटो-स्कैन रिजल्ट्स")
            st.write("हर गेम के ताज़ा रिजल्ट को खुद पकड़कर उसके अगले सिंगल नंबर का अलग बॉक्स और सबसे नीचे मास्टर कंबाइंड बॉक्स:")

            all_game_singles = []

            for col in available_cols:
                valid_series = df[col].dropna()
                if not valid_series.empty:
                    last_val = int(valid_series.iloc[-1])
                    formatted_last = f"{last_val:02d}"
                    
                    game_next_nums = []
                    for r_idx in range(len(df) - 1):
                        val = df.loc[r_idx, col]
                        if pd.notna(val) and int(val) == last_val:
                            nx_val = df.loc[r_idx + 1, col]
                            if pd.notna(nx_val):
                                game_next_nums.append(int(nx_val))
                    
                    with st.expander(f"📍 मार्केट / गेम: {col} (ताज़ा रिजल्ट: {formatted_last})", expanded=True):
                        if game_next_nums:
                            g_series = pd.Series(game_next_nums).value_counts()
                            best_n = g_series.index[0]
                            best_cnt = g_series.iloc[0]
                            
                            formatted_best = f"{best_n:02d}"
                            all_game_singles.append(formatted_best)
                            
                            col_box1, col_box2 = st.columns([2, 3])
                            with col_box1:
                                st.success(f"👑 **अगला बेस्ट सिंगल नंबर:** **{formatted_best}**")
                                st.write(f"इतिहास में यह **{best_cnt} बार** देखा गया है।")
                            with col_box2:
                                top_3_str = ", ".join([f"{k:02d} ({v} बार)" for k, v in g_series.head(3).items()])
                                st.info(f"🔥 **टॉप 3 संभावित नंबर:** {top_3_str}")
                            
                            st.markdown(f"**📋 {col} सिंगल नंबर (कॉपी करें):**")
                            st.code(formatted_best, language="text")
                        else:
                            st.warning(f"गेम {col} में नंबर {formatted_last} के बाद पर्याप्त ऐतिहासिक डेटा नहीं मिला।")
                else:
                    st.warning(f"गेम {col} में कोई वैध डेटा नहीं है।")

            # सबसे नीचे मास्टर कंबाइंड बॉक्स
            st.markdown("---")
            st.subheader("🎯 सभी छह मार्केट के सिंगल नंबरों का मास्टर कंबाइंड बॉक्स (Master Copy & Paste Box)")
            
            if all_game_singles:
                direct_combined = ", ".join(all_game_singles)
                
                palat_list = []
                for s in all_game_singles:
                    palat_list.append(s)
                    rev_s = s[::-1]
                    if rev_s != s and rev_s not in palat_list:
                        palat_list.append(rev_s)
                
                palat_combined = ", ".join(palat_list)

                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.markdown("**📋 सभी गेम के सिर्फ सिंगल नंबर (Direct Line):**")
                    st.code(direct_combined, language="text")
                with col_c2:
                    st.markdown("**📋 सभी गेम पलट के साथ (With Palat):**")
                    st.code(palat_combined, language="text")
            else:
                st.info("कॉपी करने के लिए अभी कोई सिंगल नंबर उपलब्ध नहीं है।")

        # ==========================================
        # TAB 2: ऑल-गेम क्रॉस-मार्केट पैटर्न स्कैनर
        # ==========================================
        with tab2:
            st.subheader("🔍 ऑल-गेम क्रॉस-मार्केट पैटर्न स्कैनर (Cross-Market Analysis)")
            st.write("यह टैब सभी छह मार्केट के इतिहास को एक साथ मिलाकर चेक करता है कि किसी भी गेम में ताज़ा नंबर आने के बाद कुल मिलाकर सबसे मजबूत नंबर क्या बनता है:")

            # सभी मार्केट के आखिरी रिजल्ट्स की एक कंबाइंड लिस्ट बनाना
            latest_all_results = []
            for col in available_cols:
                v_series = df[col].dropna()
                if not v_series.empty:
                    latest_all_results.append(int(v_series.iloc[-1]))

            if latest_all_results:
                st.info(f"💡 वर्तमान में सभी मार्केट के ताज़ा आखिरी नंबर: {', '.join([f'{x:02d}' for x in latest_all_results])}")
                
                cross_next_nums = []
                # पूरी टेबल में किसी भी कॉलम में ताज़ा नंबरों को ढूंढकर उनके अगले नंबर कलेक्ट करना
                for r_idx in range(len(df) - 1):
                    for col in available_cols:
                        val = df.loc[r_idx, col]
                        if pd.notna(val) and int(val) in latest_all_results:
                            nx_val = df.loc[r_idx + 1, col]
                            if pd.notna(nx_val):
                                cross_next_nums.append(int(nx_val))

                if cross_next_nums:
                    c_series = pd.Series(cross_next_nums).value_counts()
                    st.success(f"🔥 **क्रॉस-मार्केट सबसे ताकतवर अगला सिंगल नंबर:** **{c_series.index[0]:02d}** (कुल {c_series.iloc[0]} बार)")
                    
                    st.markdown("**📋 टॉप 10 क्रॉस-मार्केट संभावित नंबर (कॉपी करने के लिए):**")
                    top_10_cross = ", ".join([f"{k:02d}" for k in c_series.head(10).keys()])
                    st.code(top_10_cross, language="text")
                else:
                    st.warning("क्रॉस-मार्केट के लिए पर्याप्त ऐतिहासिक मैच नहीं मिले।")
            else:
                st.warning("कोई ताज़ा रिजल्ट उपलब्ध नहीं है।")

    else:
        st.error("CSV फ़ाइल में DB, SG, FRBD, GZBD, GALI, DSWR में से कोई भी कॉलम नहीं मिला!")
else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर दी गई जगह पर अपनी CSV फ़ाइल अपलोड करें।")
    
