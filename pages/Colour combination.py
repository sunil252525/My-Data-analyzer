import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="13-Year Pattern Search Engine", layout="wide")

st.title("🎯 13-Year Pattern & Combination Search Engine")

# 2. File Uploader Option (डायरेक्ट फाइल अपलोड करने का ऑप्शन)
st.sidebar.header("📁 Step 1: Upload Your File")
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])

@st.cache_data
def load_csv_data(file_source):
    df = pd.read_csv(file_source)
    df['DATE_DT'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y', errors='coerce')
    df = df.dropna(subset=['DATE_DT'])
    return df

# डेटा लोड करने का लॉजिक (अपलोड की गई फ़ाइल से या डिफ़ॉल्ट फ़ाइल से)
df = None

if uploaded_file is not None:
    try:
        df = load_csv_data(uploaded_file)
        st.sidebar.success("✅ Uploaded CSV Loaded Successfully!")
    except Exception as e:
        st.sidebar.error(f"Error loading uploaded file: {e}")
else:
    # अगर यूजर ने फाइल अपलोड नहीं की, तो रिपॉजिटरी में मौजूद फाइल को ढूंढने की कोशिश करेगा
    try:
        df = load_csv_data("06_10_2026 result  (1).csv")
        st.sidebar.info("ℹ️ Using default CSV from repository.")
    except Exception:
        st.warning("⚠️ कृपया बाईं तरफ (Sidebar) 'Upload CSV File' बटन पर क्लिक करके अपनी CSV फाइल अपलोड करें!")

# अगर डेटा लोड हो गया है, तभी आगे का ऐप दिखेगा
if df is not None:

    # 3. Sidebar Filters
    st.sidebar.header("🔍 Step 2: Select Pattern Filters")
    target_day = st.sidebar.slider("Select Day (तारीख)", 1, 31, 7)
    target_month = st.sidebar.slider("Select Month (महीना)", 1, 12, 10)
    
    available_years = sorted(df['DATE_DT'].dt.year.unique(), reverse=True)
    target_year = st.sidebar.selectbox("Select Target Year (साल)", available_years, index=0)

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
    tab1, tab2, tab3 = st.tabs(["1️⃣ Same Date (Yearly)", "2️⃣ 3-Month Block", "3️⃣ Cross-Month Lift"])

    # TAB 1: Same Date
    with tab1:
        st.subheader(f"📅 Pattern 1: Same Date ({target_day}/{target_month}) Across All Years")
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

    # TAB 2: 3-Month Block
    with tab2:
        st.subheader("🗓️ Pattern 2: 3-Month Block Analysis")
        m1 = target_month - 2 if target_month > 2 else target_month + 10
        m2 = target_month - 1 if target_month > 1 else 12
        m3 = target_month
        
        st.write(f"Months Sequence: **{m1} ➡️ {m2} ➡️ {m3}** | Day: **{target_day}**")
        
        block_data = []
        for yr in sorted(df['DATE_DT'].dt.year.unique(), reverse=True):
            if yr <= target_year:
                for m in [m1, m2, m3]:
                    m_yr = yr if m <= target_month else yr
                    
