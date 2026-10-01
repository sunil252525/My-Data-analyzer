import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(page_title="Game Result Analysis Dashboard", layout="wide")

st.title("📊 Game Result Analysis Dashboard")

# File Uploader
uploaded_file = st.sidebar.file_uploader("CSV फ़ाइल अपलोड करें", type=["csv"])

if uploaded_file is not None:
    # Read Dataset
    df = pd.read_csv(uploaded_file)
    
    st.subheader("📋 डेटा प्रविष्टि पूर्वावलोकन (Data Preview)")
    st.dataframe(df.head(), use_container_width=True)

    # Define Game Columns
    game_columns = [col for col in df.columns if col.lower() not in ["date", "day", "दिनांक", "दिन", "s.no", "id"]]

    # Helper function to generate family (Rashi) sets for a number
    def get_family(num):
        if pd.isna(num):
            return []
        try:
            num = int(num) % 100
        except ValueError:
            return []
        
        d1 = num // 10
        d2 = num % 10
        
        # Mirror digit mapping (Rashi)
        rashi_map = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}
        
        r1, r2 = rashi_map[d1], rashi_map[d2]
        
        family_set = {
            d1 * 10 + d2,
            d1 * 10 + r2,
            r1 * 10 + d2,
            r1 * 10 + r2
        }
        return sorted(list(family_set))

    summary_data_13 = []

    # Historical Analysis Loop for all games
    for col in game_columns:
        valid_series = pd.to_numeric(df[col], errors='coerce').dropna().astype(int)
        
        if len(valid_series) >= 10:
            last_num = valid_series.iloc[-1]
            
            # Frequency and Pattern Ranking Logic
            value_counts = valid_series.value_counts()
            ranked_nums = list(value_counts.index)
            
            # Extract top ranked predictions
            top_1_special = ranked_nums[0]
            top_3_special = ranked_nums[:3]
            top_6_special = ranked_nums[:6]
            top_10_special = ranked_nums[:10]
            
            # Family calculations
            top_1_fam = get_family(top_1_special)
            top_3_fams = sorted(list(set([f for n in top_3_special for f in get_family(n)])))
            
            summary_data_13.append({
                "गेम का नाम": col,
                "हालिया रिज़ल्ट": f"{last_num:02d}",
                "👑 1 स्पेशल (Single Best)": f"{top_1_special:02d}",
                "🔥 1 स्पेशल की फैमिली (8 जोड़ी)": ", ".join([f"{x:02d}" for x in top_1_fam]),
                "🎯 3 स्पेशल नंबर": ", ".join([f"{x:02d}" for x in top_3_special]),
                "👑 3 स्पेशल की कुल फैमिली": ", ".join([f"{x:02d}" for x in top_3_fams]),
                "⚡ 6 स्पेशल नंबर": ", ".join([f"{x:02d}" for x in top_6_special]),
                "📋 10 स्पेशल नंबर": ", ".join([f"{x:02d}" for x in top_10_special])
            })

    if summary_data_13:
        st.success("✅ **सभी 6 गेमों के ऐतिहासिक विश्लेषण से निकले प्रीमियर सिलेक्टेड नंबर (फ़ॉर्मूला 3 और 4 कंबाइंड):**")
        st.dataframe(pd.DataFrame(summary_data_13), use_container_width=True)
    else:
        st.warning("पर्याप्त डेटा उपलब्ध नहीं है या कॉलम सही प्रारूप में नहीं हैं।")

else:
    st.info("👈 डैशबोर्ड शुरू करने के लिए ऊपर बाईं ओर (Sidebar) से अपनी CSV फ़ाइल अपलोड करें।")
