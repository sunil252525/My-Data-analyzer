import streamlit as st
import pandas as pd

st.set_page_config(page_title="Deep Pattern Analyzer", layout="wide")

st.title("📊 Deep Historical Pattern & Analytics Engine")
st.write("अपनी CSV फ़ाइल अपलोड करें और 13 साल के ऐतिहासिक डेटा का विश्लेषण देखें।")

uploaded_file = st.file_uploader("अपनी CSV फ़ाइल यहाँ अपलोड करें", type=["csv"])

def get_family(num):
    try:
        num = int(num)
        d1, d2 = num // 10, num % 10
        r1, r2 = (d1 + 5) % 10, (d2 + 5) % 10
        fam = set()
        for a, b in [(d1, d2), (d1, r2), (r1, d2), (r1, r2)]:
            fam.add(a * 10 + b)
            fam.add(b * 10 + a)
        return sorted(list(fam))
    except:
        return []

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    st.success("फ़ाइल सफलतापूर्वक लोड हो गई!")
    
    st.subheader("📋 हालिया डेटा (Recent Entries)")
    st.dataframe(df.dropna(how='all', subset=cols).tail(10))
    
    st.sidebar.header("विश्लेषण विकल्प (Options)")
    target_game = st.sidebar.selectbox("गेम चुनें (Select Game)", cols)
    search_num = st.sidebar.number_input("लास्ट रिजल्ट (Target Number)", min_value=0, max_value=99, value=71)
    
    if st.sidebar.button("विश्लेषण शुरू करें (Run Analysis)"):
        st.subheader(f"🔍 {target_game} में नंबर '{search_num}' का 13 साल का विश्लेषण")
        
        target_indices = df[df[target_game] == search_num].index
        total_count = len(target_indices)
        
        st.metric(label="इतिहास में कुल बार आया (Total Count)", value=f"{total_count} बार")
        
        if total_count > 0:
            next_day_vals = df.loc[target_indices + 1, target_game].dropna()
            
            st.markdown("### 1-Day Follow-up (अगले दिन के टॉप नंबर)")
            st.dataframe(next_day_vals.value_counts().head(10).reset_index().rename(columns={'count': 'बार आया (Count)'}))
            
            st.markdown("### 👨‍👩‍👧‍👦 टॉप 8-नंबर फैमिलियाँ (Top Families)")
            fam_counts = {}
            for val in next_day_vals:
                fam = tuple(get_family(val))
                if fam:
                    fam_counts[fam] = fam_counts.get(fam, 0) + 1
            
            fam_df = pd.DataFrame([
                {"फैमिली की पहली संख्या": f[0], "पूरी फैमिली": str(f), "इतिहास में बार आए": cnt, "सफलता दर (%)": round((cnt/len(next_day_vals))*100, 1)}
                for f, cnt in sorted(fam_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            ])
            st.table(fam_df)
            
            st.markdown("### 🎯 हर्फ़ विश्लेषण (Haruf Frequency)")
            in_h = next_day_vals.apply(lambda x: int(x) // 10).value_counts().head(3)
            out_h = next_day_vals.apply(lambda x: int(x) % 10).value_counts().head(3)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**अंदर हर्फ़ (Inside Haruf Top 3):**")
                st.json(in_h.to_dict())
            with col2:
                st.write("**बाहर हर्फ़ (Outside Haruf Top 3):**")
                st.json(out_h.to_dict())
