import streamlit as st
import pandas as pd

# 1. स्ट्रीमलिट पेज कंफीग्रेशन (यह हमेशा सबसे ऊपर होना चाहिए)
st.set_page_config(page_title="13-Year Pattern & Combination Analyzer", layout="wide")

st.title("🎯 13-Year Pattern & Combination Search Engine")

# 2. CSV डेटा लोड करना
@st.cache_data
def load_data():
    # अपनी CSV फाइल का सही नाम यहाँ दें
    df = pd.read_csv("06_10_2026 result  (1).csv")
    df['DATE_DT'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y', errors='coerce')
    df = df.dropna(subset=['DATE_DT'])
    return df

try:
    df = load_data()
    st.sidebar.success("✅ डेटा सफलता से लोड हो गया!")
except Exception as e:
    st.error(f"❌ डेटा लोड करने में समस्या आई: {e}")
    st.stop()

# 3. साइडबार में तारीख, महीना और साल चुनने के फिल्टर
st.sidebar.header("🔍 फिल्टर सेट करें")
target_day = st.sidebar.slider("तारीख (Day):", 1, 31, 7)
target_month = st.sidebar.slider("महीना (Month):", 1, 12, 10)
target_year = st.sidebar.selectbox("साल (Target Year):", list(range(2026, 2012, -1)), index=1)

# 4. 10 फैमिली कॉम्बिनेशन
FAMILY_GROUPS = {
    "Fam_01": ['01', '10', '51', '15', '06', '60', '56', '65'],
    "Fam_02": ['02', '20', '52', '25', '07', '70', '57', '75'],
    "Fam_03": ['03', '30', '53', '35', '08', '80', '58', '85'],
    "Fam_04": ['04', '40', '54', '45', '09', '90', '59', '95'],
    "Fam_11": ['11', '61', '16', '66'],
    "Fam_12": ['12', '21', '62', '26', '17', '71', '67', '76'],
    "Fam_13": ['13', '31', '63', '36', '18', '81', '68', '86'],
    "Fam_14": ['14', '41', '64', '46', '19', '91', '69', '96'],
    "Fam_23": ['23', '32', '73', '37', '28', '82', '78', '87'],
    "Fam_24": ['24', '42', '74', '47', '29', '92', '79', '97']
}

def clean_num(val):
    if pd.isna(val) or str(val).strip().lower() in ['xx', 'nan', '']:
        return None
    try:
        return str(int(float(val))).zfill(2)
    except:
        return str(val).strip().zfill(2)

def get_family(num_str):
    if not num_str:
        return "N/A"
    for fam_name, members in FAMILY_GROUPS.items():
        if num_str in members:
            return fam_name
    return "Other"

# 5. तीनों पैटर्न के लिए अलग-अलग टैब
tab1, tab2, tab3 = st.tabs(["1️⃣ Same Date (Yearly)", "2️⃣ 3-Month Block", "3️⃣ Cross-Month Lift"])

# --- TAB 1: हर साल की सेम डेट का पैटर्न ---
with tab1:
    st.subheader(f"📅 Pattern 1: {target_day}/{target_month} तारीख का 13 साल का इतिहास")
    same_date_df = df[(df['DATE_DT'].dt.day == target_day) & (df['DATE_DT'].dt.month == target_month)].sort_values('DATE_DT', ascending=False)
    
    table_data = []
    for _, row in same_date_df.iterrows():
        yr = row['DATE_DT'].year
        fb, gb, gl, ds = clean_num(row['FRBD']), clean_num(row['GZBD']), clean_num(row['GALI']), clean_num(row['DSWR'])
        table_data.append({
            "Year": yr,
            "FRBD": f"{fb or 'XX'} ({get_family(fb)})",
            "GZBD": f"{gb or 'XX'} ({get_family(gb)})",
            "GALI": f"{gl or 'XX'} ({get_family(gl)})",
            "DSWR": f"{ds or 'XX'} ({get_family(ds)})"
        })
    st.dataframe(pd.DataFrame(table_data), use_container_width=True)

# --- TAB 2: 3-मंथ ब्लॉक पैटर्न ---
with tab2:
    st.subheader(f"🗓️ Pattern 2: 3-मंथ सीक्वेंस (पिछले 2 महीने + चालू महीना)")
    m1 = target_month - 2 if target_month > 2 else target_month + 10
    m2 = target_month - 1 if target_month > 1 else 12
    m3 = target_month
    
    st.write(f"चेक हो रहे महीने: **महीना {m1} ➡️ महीना {m2} ➡️ महीना {m3}** (तारीख: **{target_day}**)")
    
    block_data = []
    for yr in range(target_year, 2012, -1):
        for m in [m1, m2, m3]:
            m_yr = yr if m <= target_month else yr - 1
            m_df = df[(df['DATE_DT'].dt.year == m_yr) & (df['DATE_DT'].dt.month == m) & (df['DATE_DT'].dt.day == target_day)]
            if not m_df.empty:
                r = m_df.iloc[0]
                fb, gb, gl, ds = clean_num(r['FRBD']), clean_num(r['GZBD']), clean_num(r['GALI']), clean_num(r['DSWR'])
                block_data.append({
                    "Year": m_yr,
                    "Month": m,
                    "Day": target_day,
                    "FRBD": f"{fb or 'XX'} ({get_family(fb)})",
                    "GZBD": f"{gb or 'XX'} ({get_family(gb)})",
                    "GALI": f"{gl or 'XX'} ({get_family(gl)})",
                    "DSWR": f"{ds or 'XX'} ({get_family(ds)})"
                })
    st.dataframe(pd.DataFrame(block_data), use_container_width=True)

# --- TAB 3: क्रॉस-मंथ लिफ्ट पैटर्न ---
with tab3:
    st.subheader(f"🔀 Pattern 3: पिछले महीने से नंबर/फैमिली का उठना")
    prev_m = target_month - 1 if target_month > 1 else 12
    prev_m_yr = target_year if target_month > 1 else target_year - 1
    
    st.write(f"चेक हो रहा है: क्या **{target_day}/{target_month}/{target_year}** का नंबर **महीने {prev_m}/{prev_m_yr} की 22 से 28 तारीख** से उठा है?")
    
    p_data = df[(df['DATE_DT'].dt.year == prev_m_yr) & (df['DATE_DT'].dt.month == prev_m) & (df['DATE_DT'].dt.day.between(22, 28))]
    c_data = df[(df['DATE_DT'].dt.year == target_year) & (df['DATE_DT'].dt.month == target_month) & (df['DATE_DT'].dt.day == target_day)]
    
    if c_data.empty:
        st.info("चुनी हुई तारीख का इस साल में अभी रिजल्ट नहीं आया है।")
    else:
        c_row = c_data.iloc[0]
        c_nums = { "FB": clean_num(c_row['FRBD']), "GB": clean_num(c_row['GZBD']), "GL": clean_num(c_row['GALI']), "DS": clean_num(c_row['DSWR']) }
        
        matches = []
        for _, p_row in p_data.iterrows():
            p_day = p_row['DATE_DT'].day
            p_nums = { "FB": clean_num(p_row['FRBD']), "GB": clean_num(p_row['GZBD']), "GL": clean_num(p_row['GALI']), "DS": clean_num(p_row['DSWR']) }
            
            for c_game, cn in c_nums.items():
                for p_game, pn in p_nums.items():
                    if cn and pn:
                        if cn == pn:
                            matches.append(f"🔥 **सिंगल नंबर मैच**: पिछले महीने की तारीख {p_day} ({p_game}: {pn}) ➡️ चालू तारीख {target_day} ({c_game}: {cn})")
                        elif get_family(cn)
    
