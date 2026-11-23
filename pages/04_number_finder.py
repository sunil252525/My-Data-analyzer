"""
=============================================================================
📱 ऐप का नाम: Tabbed Multi-Market All-Game Corrected Pattern Matcher
-----------------------------------------------------------------------------
💡 मुख्य विशेषताएँ:
- टैब 1: हर गेम का अलग-अलग ऑटो-स्कैन और मास्टर कंबाइंड बॉक्स (हर गेम की एक लाइन में नंबर + पलट)
- टैब 2: सही 'फ्लैटेंड ऑल-गेम सीक्वेंस' लॉजिक के साथ ताज़ा नंबर का डीप स्कैनर
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np

# --- Page Configuration ---
st.set_page_config(page_title="Multi-Tab Corrected Pattern Matcher", layout="wide")

st.title("🎯 एडवांस्ड ऑल-इन-वन पैटर्न और सिंगल स्कैनर (सटीक संशोधित संस्करण)")
st.write("यह ऐप सही ऑल-गेम क्रमिक (Sequential) लॉजिक के साथ पैटर्न स्कैन करता है।")

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
        
        # --- दो स्पष्ट टैब ---
        tab1, tab2 = st.tabs([
            "⚡ 1. हर गेम का अलग-अलग ऑटो-स्कैन और मास्टर बॉक्स", 
            "🔍 2. ताज़ा नंबर का 'ऑल-गेम' सटीक क्रमिक स्कैनर"
        ])
        
        # ==========================================
        # TAB 1: गेम-वाइज सेपरेट ऑटो-स्कैन और मास्टर बॉक्स
        # ==========================================
        with tab1:
            st.subheader("📊 सभी छह मार्केट के अलग-अलग ऑटो-स्कैन रिजल्ट्स")
            
            all_game_singles = []
            all_games_compact_lines = []  # हर गेम की एक लाइन (टॉप 3 + उनकी पलट साथ में)

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
                            
                            # टॉप 3 नंबर और उन्हीं की पलट एक ही लाइन में जोड़ना
                            top3_list = [f"{k:02d}" for k in g_series.head(3).keys()]
                            line_items = list(top3_list)
                            for num_str in top3_list:
                                rev_str = num_str[::-1]
                                if rev_str not in line_items:
                                    line_items.append(rev_str)
                            
                            all_games_compact_lines.append(", ".join(line_items))
                            
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
                    st.code(pal_combined, language="text")
                
                # --- सबसे लास्ट वाला बॉक्स: हर गेम के 3 नंबर + उनकी पलट एक ही लाइन में ---
                if all_games_compact_lines:
                    st.markdown("**📋 सभी गेम के नंबर और पलट (हर गेम की एक लाइन में):**")
                    compact_box_text = "\n".join(all_games_compact_lines)
                    st.code(compact_box_text, language="text")
            else:
                st.info("कॉपी करने के लिए अभी कोई सिंगल नंबर उपलब्ध नहीं है।")

        # ==========================================
        # TAB 2: ताज़ा नंबर का 'ऑल-गेम' सटीक क्रमिक स्कैनर (Corrected Flat Sequence Logic)
        # ==========================================
        with tab2:
            st.subheader("🔍 ताज़ा नंबर का 'ऑल-गेम' सटीक क्रमिक स्कैनर (Sequential All-Market Deep Matcher)")
            st.write("यह टैब सभी छह मार्केट के डेटा को सही क्रमानुसार (Sequence में) जोड़कर चेक करता है कि किसी भी ताज़ा नंबर के बाद ऑल-गेम में ठीक अगला नंबर क्या आया है:")

            # 1. पूरी टेबल को क्रमानुसार एक लंबी लिस्ट (Flat List) में बदलना ताकि मार्केट-दर-मार्केट सही क्रम बना रहे
            flat_sequence = []
            for r_idx in range(len(df)):
                for c_name in available_cols:
                    val = df.loc[r_idx, c_name]
                    if pd.notna(val):
                        flat_sequence.append(int(val))

            # 2. हर गेम का आखिरी (ताज़ा) नंबर निकालना
            game_latest_dict = {}
            for col in available_cols:
                v_series = df[col].dropna()
                if not v_series.empty:
                    game_latest_dict[col] = int(v_series.iloc[-1])

            if game_latest_dict and len(flat_sequence) > 1:
                latest_str_list = [f"{g}: {n:02d}" for g, n in game_latest_dict.items()]
                st.info(f"💡 **हर गेम का ताज़ा रिजल्ट:** {', '.join(latest_str_list)}")

                all_game_breakdown = []
                master_all_game_nexts = []

                # 3. हर गेम के ताज़ा नंबर को इस लंबी क्रमिक लिस्ट में ढूंढकर उसके ठीक बाद आने वाले नंबर देखना
                for col, target_val in game_latest_dict.items():
                    market_all_nexts = []
                    
                    for i in range(len(flat_sequence) - 1):
                        if flat_sequence[i] == target_val:
                            nx_val = flat_sequence[i + 1]
                            market_all_nexts.append(nx_val)
                            master_all_game_nexts.append(nx_val)

                    if market_all_nexts:
                        top_m = pd.Series(market_all_nexts).value_counts().index[0]
                        top_count = pd.Series(market_all_nexts).value_counts().iloc[0]
                        all_game_breakdown.append({
                            "गेम & ताज़ा नंबर": f"{col} ({target_val:02d})",
                            "ऑल-गेम में सबसे पक्का अगला नंबर": f"{top_m:02d}",
                            "कुल बार देखा गया": f"{top_count} बार"
                        })
                    else:
                        all_game_breakdown.append({
                            "गेम & ताज़ा नंबर": f"{col} ({target_val:02d})",
                            "ऑल-गेम में सबसे पक्का अगला नंबर": "डाटा नहीं",
                            "कुल बार देखा गया": "-"
                        })

                if all_game_breakdown:
                    st.markdown("### 📊 हर गेम के ताज़ा नंबर के बाद 'ऑल-गेम' क्रमिक इतिहास का रिजल्ट:")
                    res_df_all = pd.DataFrame(all_game_breakdown)
                    st.dataframe(res_df_all, use_container_width=True, hide_index=True)
                    
                    valid_all_singles = [row['ऑल-गेम में सबसे पक्का अगला नंबर'] for row in all_game_breakdown if row['ऑल-गेम में सबसे पक्का अगला नंबर'] != "डाटा नहीं"]
                    if valid_all_singles:
                        st.markdown("**📋 इन सभी ऑल-गेम सिंगल नंबरों की कंबाइंड लाइन (कॉपी करें):**")
                        st.code(", ".join(valid_all_singles), language="text")

                if master_all_game_nexts:
                    m_series = pd.Series(master_all_game_nexts).value_counts()
                    st.markdown("---")
                    st.success(f"🔥 **इन सबका महा-संयोजन (Overall All-Game Top Single):** **{m_series.index[0]:02d}** (कुल {m_series.iloc[0]} बार ऑल-गेम क्रम में आया है)")
                    
                    st.markdown("**📋 ऑल-गेम के टॉप 10 सबसे ताकतवर नंबर (कॉपी करने के लिए):**")
                    top_10_all = ", ".join([f"{k:02d}" for k in m_series.head(10).keys()])
                    st.code(top_10_all, language="text")
                else:
                    st.warning("ऑल-गेम के लिए पर्याप्त क्रमिक ऐतिहासिक मैच नहीं मिले।")
            else:
                st.warning("कोई ताज़ा रिजल्ट उपलब्ध नहीं है।")

    else:
        st.error("CSV फ़ाइल में DB, SG, FRBD, GZBD, GALI, DSWR में से कोई भी कॉलम नहीं मिला!")
else:
    st.info("कृपया आगे बढ़ने के लिए ऊपर दी गई जगह पर अपनी CSV फ़ाइल अपलोड करें।")
    
