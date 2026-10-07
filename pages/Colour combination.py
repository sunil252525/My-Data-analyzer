import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="13-Year Pattern Search", layout="wide")

st.title("🎯 13-Year Pattern & Combination Analyzer")

# 2. Data Loading
@st.cache_data
def load_data():
    df = pd.read_csv("06_10_2026 result  (1).csv")
    df['DATE_DT'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y', errors='coerce')
    df = df.dropna(subset=['DATE_DT'])
    return df

try:
    df = load_data()
    st.sidebar.success("Data Loaded Successfully!")
except Exception as e:
    st.error(f"Error loading file: {e}")
    st.stop()

# 3. Sidebar Inputs
st.sidebar.header("Filter Settings")
target_day = st.sidebar.slider("Select Day", 1, 31, 7)
target_month = st.sidebar.slider("Select Month", 1, 12, 10)
target_year = st.sidebar.selectbox("Select Target Year", list(range(2026, 2012, -1)), index=1)

# 4. Family Mapping
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

# 5. UI Tabs
tab1, tab2, tab3 = st.tabs(["1. Same Date (Yearly)", "2. 3-Month Block", "3. Cross-Month Lift"])

with tab1:
    st.subheader(f"Pattern 1: Same Date ({target_day}/{target_month}) Across Years")
    same_date_df = df[(df['DATE_DT'].dt.day == target_day) & (df['DATE_DT'].dt.month == target_month)].sort_values('DATE_DT', ascending=False)
    
    table_data = []
    for _, row in same_date_df.iterrows():
        yr = row['DATE_DT'].year
        fb = clean_num(row['FRBD'])
        gb = clean_num(row['GZBD'])
        gl = clean_num(row['GALI'])
        ds = clean_num(row['DSWR'])
        table_data.append({
            "Year": yr,
            "FRBD": f"{fb or 'XX'} ({get_family(fb)})",
            "GZBD": f"{gb or 'XX'} ({get_family(gb)})",
            "GALI": f"{gl or 'XX'} ({get_family(gl)})",
            "DSWR": f"{ds or 'XX'} ({get_family(ds)})"
        })
    st.dataframe(pd.DataFrame(table_data), use_container_width=True)

with tab2:
    st.subheader("Pattern 2: 3-Month Block Analysis")
    m1 = target_month - 2 if target_month > 2 else target_month + 10
    m2 = target_month - 1 if target_month > 1 else 12
    m3 = target_month
    
    st.write(f"Months: **{m1} -> {m2} -> {m3}** | Day: **{target_day}**")
    
    block_data = []
    for yr in range(target_year, 2012, -1):
        for m in [m1, m2, m3]:
            m_yr = yr if m <= target_month else yr - 1
            m_df = df[(df['DATE_DT'].dt.year == m_yr) & (df['DATE_DT'].dt.month == m) & (df['DATE_DT'].dt.day == target_day)]
            if not m_df.empty:
                r = m_df.iloc[0]
                fb = clean_num(r['FRBD'])
                gb = clean_num(r['GZBD'])
                gl = clean_num(r['GALI'])
                ds = clean_num(r['DSWR'])
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

with tab3:
    st.subheader("Pattern 3: Cross-Month Lift")
    prev_m = target_month - 1 if target_month > 1 else 12
    prev_m_yr = target_year if target_month > 1 else target_year - 1
    
    st.write(f"Comparing **{target_day}/{target_month}/{target_year}** with **Month {prev_m}/{prev_m_yr} (Dates 22-28)**")
    
    p_data = df[(df['DATE_DT'].dt.year == prev_m_yr) & (df['DATE_DT'].dt.month == prev_m) & (df['DATE_DT'].dt.day.between(22, 28))]
    c_data = df[(df['DATE_DT'].dt.year == target_year) & (df['DATE_DT'].dt.month == target_month) & (df['DATE_DT'].dt.day == target_day)]
    
    if c_data.empty:
        st.info("No data yet for target date in selected year.")
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
                            matches.append(f"EXACT MATCH: Prev Month Day {p_day} ({p_game}: {pn}) -> Target Day {target_day} ({c_game}: {cn})")
                        elif get_family(cn) == get_family(pn) and get_family(cn) != "Other":
                            matches.append(f"FAMILY MATCH ({get_family(cn)}): Prev Month Day {p_day} ({p_game}: {pn}) -> Target Day {target_day} ({c_game}: {cn})")
        
        if matches:
            for m in matches:
                st.write(m)
        else:
            st.warning("No direct or family matches found from previous month dates 22-28.")
            
