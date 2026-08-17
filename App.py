import streamlit as st
import pandas as pd

st.set_page_config(page_title="Advanced Pattern & Logic Engine", layout="wide")

st.title("🎯 Advanced Pattern & Logic Engine")
st.write("अपने 13 साल के डेटा पर कस्टम लॉजिक्स, योग, प्लस-माइनस और डेट ट्रेंड्स एनालाइज करें।")

uploaded_file = st.file_uploader("अपनी CSV फ़ाइल अपलोड करें", type=["csv"])

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

def get_digit_sum(num):
    try:
        num = int(num)
        d1, d2 = num // 10, num % 10
        return (d1 + d2) % 10
    except:
        return None

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    if 'DATE' in df.columns:
        df['DATE_DT'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y', errors='coerce')
        df['DAY'] = df['DATE_DT'].dt.day_name()
        df['DAY_NUM'] = df['DATE_DT'].dt.day
    
    st.success("फ़ाइल सफलतापूर्वक लोड हो गई!")

    tab1, tab2, tab3, tab4 = st.tabs([
        "1️⃣ 2-Day Range Analysis", 
        "2️⃣ Monthly Date & Day Trends", 
        "3️⃣ Plus/Minus Patterns", 
        "4️⃣ Sum/Total (योग) & Haruf"
    ])

    # ---------------- TAB 1 ----------------
    with tab1:
        st.subheader("📌 टारगेट नंबर आने के 2 दिनों के अंदर का एनालिसिस")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            g1 = st.selectbox("गेम चुनें", cols, key="t1_g")
        with col_t2:
            num1 = st.number_input("टारगेट नंबर", min_value=0, max_value=99, value=71, key="t1_n")
        
        if st.button("2-Day एनालिसिस चलाएं"):
            idx_list = df[df[g1] == num1].index
            next_1day, next_2day = [], []
            for idx in idx_list:
                if idx + 1 < len(df) and pd.notna(df.loc[idx + 1, g1]):
                    next_1day.append(df.loc[idx + 1, g1])
                if idx + 2 < len(df) and pd.notna(df.loc[idx + 2, g1]):
                    next_2day.append(df.loc[idx + 2, g1])
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### 🔹 Day 1 (अगले दिन के टॉप 5 नंबर)")
                st.dataframe(pd.Series(next_1day).value_counts().head(5).reset_index(name='बार आया'))
            with c2:
                st.markdown("### 🔹 Day 2 (दूसरे दिन के टॉप 5 नंबर)")
                st.dataframe(pd.Series(next_2day).value_counts().head(5).reset_index(name='बार आया'))

    # ---------------- TAB 2 ----------------
    with tab2:
        st.subheader("📅 तारीख (Date) और दिन (Day) के अनुसार ट्रेंड्स")
        c_date1, c_date2 = st.columns(2)
        with c_date1:
            sel_day_num = st.slider("महीने की तारीख चुनें (1-31)", 1, 31, 15)
        with c_date2:
            sel_game2 = st.selectbox("गेम सेलेक्ट करें", cols, key="t2_g")
        
        if 'DAY_NUM' in df.columns:
            filtered_df = df[df['DAY_NUM'] == sel_day_num][sel_game2].dropna()
            st.write(f"**हर महीने की {sel_day_num} तारीख को {sel_game2} में सबसे ज्यादा आने वाले नंबर:**")
            st.dataframe(filtered_df.value_counts().head(10).reset_index(name='इतिहास में कुल बार'))

    # ---------------- TAB 3 ----------------
    with tab3:
        st.subheader("➕➖ दो गेम का प्लस-माइनस (Cross Game Plus-Minus Analysis)")
        c_pm1, c_pm2, c_pm3 = st.columns(3)
        with c_pm1:
            g_a = st.selectbox("पहला गेम (Game A)", cols, index=4, key="pm_a")
        with c_pm2:
            g_b = st.selectbox("दूसरा गेम (Game B)", cols, index=5, key="pm_b")
        with c_pm3:
            diff_val = st.number_input("प्लस/माइनस वैल्यू (+/-)", min_value=1, max_value=10, value=1)
        
        if st.button("प्लस-माइनस पैटर्न चेक करें"):
            temp_df = df[[g_a, g_b]].dropna()
            plus_matches = (temp_df[g_b] == (temp_df[g_a] + diff_val) % 100).sum()
            minus_matches = (temp_df[g_b] == (temp_df[g_a] - diff_val) % 100).sum()
            
            st.metric(f"{g_a} में +{diff_val} होकर {g_b} में पास हुआ", f"{plus_matches} बार")
            st.metric(f"{g_a} में -{diff_val} होकर {g_b} में पास हुआ", f"{minus_matches} बार")

    # ---------------- TAB 4 ----------------
    with tab4:
        st.subheader("🧮 अंक योग (Digit Sum/Total) और हर्फ़ का विश्लेषण")
        c_s1, c_s2 = st.columns(2)
        with c_s1:
            g_sum = st.selectbox("गेम चुनें", cols, key="t4_g")
        with c_s2:
            target_sum = st.slider("पहला योग (Target Sum: 0-9)", 0, 9, 8)
        
        if st.button("योग (Sum) का विश्लेषण करें"):
            df['SUM'] = df[g_sum].apply(get_digit_sum)
            matching_idx = df[df['SUM'] == target_sum].index
            
            next_sums = []
            for idx in matching_idx:
                if idx + 1 < len(df) and pd.notna(df.loc[idx + 1, 'SUM']):
                    next_sums.append(int(df.loc[idx + 1, 'SUM']))
            
            st.write(f"जब **{g_sum}** में अंकों का योग **{target_sum}** आया, तो अगले दिन का योग क्या रहा:")
            st.dataframe(pd.Series(next_sums).value_counts().reset_index().rename(columns={'index': 'अगला योग', 0: 'इतिहास में बार आया'}))
