import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Auto Pattern Search Engine", layout="wide")

st.title("🎯 Auto 13-Year Pattern & Origin Tracker")

# 2. Sidebar File Upload
st.sidebar.header("📁 Upload Your Result CSV")
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])

@st.cache_data
def load_csv_data(file_source):
    df = pd.read_csv(file_source)
    df['DATE_DT'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y', errors='coerce')
    df = df.dropna(subset=['DATE_DT']).sort_values('DATE_DT')
    return df

df = None

if uploaded_file is not None:
    try:
        df = load_csv_data(uploaded_file)
        st.sidebar.success("✅ File Loaded Successfully!")
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")
else:
    try:
        df = load_csv_data("06_10_2026 result  (1).csv")
        st.sidebar.info("ℹ️ Using default repository CSV")
    except Exception:
        st.warning("⚠️ Kripya sidebar se 'Upload CSV File' button se CSV file upload karein!")

if df is not None and not df.empty:

    # 3. Auto Detect Latest Date
    valid_data_df = df.dropna(subset=['FRBD', 'GZBD', 'GALI', 'DSWR'], how='all')
    
    if not valid_data_df.empty:
        latest_row = valid_data_df.iloc[-1]
        default_day = int(latest_row['DATE_DT'].day)
        default_month = int(latest_row['DATE_DT'].month)
        default_year = int(latest_row['DATE_DT'].year)
    else:
        default_day, default_month, default_year = 6, 10, 2026

    # Session State Controls
    if 'target_day' not in st.session_state:
        st.session_state.target_day = default_day
    if 'target_month' not in st.session_state:
        st.session_state.target_month = default_month

    st.info(f"📌 **Auto-Detected Date:** {st.session_state.target_day}/{st.session_state.target_month}/{default_year}")

    # Sidebar Controls (+ / -)
    st.sidebar.header("⚙️ Date Controls (+ / -)")

    col_d1, col_d2, col_d3 = st.sidebar.columns([1, 2, 1])
    if col_d1.button("➖ Day"):
        if st.session_state.target_day > 1: st.session_state.target_day -= 1
    col_d2.markdown(f"<h3 style='text-align: center; margin:0;'>{st.session_state.target_day}</h3>", unsafe_allow_html=True)
    if col_d3.button("➕ Day"):
        if st.session_state.target_day < 31: st.session_state.target_day += 1

    col_m1, col_m2, col_m3 = st.sidebar.columns([1, 2, 1])
    if col_m1.button("➖ Month"):
        if st.session_state.target_month > 1: st.session_state.target_month -= 1
    col_m2.markdown(f"<h3 style='text-align: center; margin:0;'>{st.session_state.target_month}</h3>", unsafe_allow_html=True)
    if col_m3.button("➕ Month"):
        if st.session_state.target_month < 12: st.session_state.target_month += 1

    available_years = sorted(df['DATE_DT'].dt.year.unique(), reverse=True)
    target_year = st.sidebar.selectbox("Select Target Year", available_years, index=0)

    target_day = st.session_state.target_day
    target_month = st.session_state.target_month

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
        if pd.isna(val) or str(val).strip().lower() in ['xx', 'nan', '']: return None
        try: return str(int(float(val))).zfill(2)
        except Exception: return str(val).strip().zfill(2)

    def get_family(num_str):
        if not num_str: return "N/A"
        for fam_name, members in FAMILY_GROUPS.items():
            if num_str in members: return fam_name
        return "Other"

    # UI Tabs
    tab1, tab2, tab3 = st.tabs(["1️⃣ Same Date (Yearly)", "2️⃣ 3-Month Sequence", "3️⃣ Origin Tracker (कहाँ से उठाया)"])

    # TAB 1
    with tab1:
        st.subheader(f"📅 Date {target_day}/{target_month} Across All Years")
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

    # TAB 2
    with tab2:
        m1 = target_month - 2 if target_month > 2 else target_month + 10
        m2 = target_month - 1 if target_month > 1 else 12
        m3 = target_month
        st.subheader(f"🗓️ 3-Month Sequence (Month {m1} ➡️ {m2} ➡️ {m3})")

        for yr in range(target_year, target_year - 4, -1):
            st.write(f"**वर्ष {yr} (तारीख {target_day}):**")
            block_rows = []
            for m in [m1, m2, m3]:
                m_yr = yr if m <= target_month else yr - 1
                m_df = df[(df['DATE_DT'].dt.year == m_yr) & (df['DATE_DT'].dt.month == m) & (df['DATE_DT'].dt.day == target_day)]
                if not m_df.empty:
                    r = m_df.iloc[0]
                    fb, gb, gl, ds = clean_num(r['FRBD']), clean_num(r['GZBD']), clean_num(r['GALI']), clean_num(r['DSWR'])
                    block_rows.append({
                        "Month": f"{m}/{m_yr}",
                        "FRBD": f"{fb or 'XX'} ({get_family(fb)})",
                        "GZBD": f"{gb or 'XX'} ({get_family(gb)})",
                        "GALI": f"{gl or 'XX'} ({get_family(gl)})",
                        "DSWR": f"{ds or 'XX'} ({get_family(ds)})"
                    })
            if block_rows:
                st.dataframe(pd.DataFrame(block_rows), use_container_width=True)

    # TAB 3: ORIGIN TRACKER (यह ढूँढेगा कि किस तारीख से उठाया गया है)
    with tab3:
        st.subheader(f"🔍 Origin Tracker: हर साल {target_day}/{target_month} का नंबर पिछले महीने में किस तारीख से उठा है?")
        
        origin_results = []
        
        for yr in range(target_year, target_year - 6, -1):
            prev_m = target_month - 1 if target_month > 1 else 12
            prev_m_yr = yr if target_month > 1 else yr - 1
            
            # Today's Result
            curr_df = df[(df['DATE_DT'].dt.year == yr) & (df['DATE_DT'].dt.month == target_month) & (df['DATE_DT'].dt.day == target_day)]
            
            # Previous Month's Full Result
            prev_df = df[(df['DATE_DT'].dt.year == prev_m_yr) & (df['DATE_DT'].dt.month == prev_m)]
            
            if not curr_df.empty and not prev_df.empty:
                c_row = curr_df.iloc[0]
                c_games = {"FB": clean_num(c_row['FRBD']), "GB": clean_num(c_row['GZBD']), "GL": clean_num(c_row['GALI']), "DS": clean_num(c_row['DSWR'])}
                
                matched_dates = []
                for _, p_row in prev_df.iterrows():
                    p_day = p_row['DATE_DT'].day
                    p_games = {"FB": clean_num(p_row['FRBD']), "GB": clean_num(p_row['GZBD']), "GL": clean_num(p_row['GALI']), "DS": clean_num(p_row['DSWR'])}
                    
                    for cg, cn in c_games.items():
                        if cn:
                            cfam = get_family(cn)
                            for pg, pn in p_games.items():
                                if pn and (cn == pn or (cfam == get_family(pn) and cfam != "Other")):
                                    match_type = "Single Exact" if cn == pn else f"Family ({cfam})"
                                    matched_dates.append(f"तारीख {p_day} ({pg}: {pn} -> {cg}: {cn}) [{match_type}]")
                
                if matched_dates:
                    origin_results.append({
                        "Year": yr,
                        "Target Date": f"{target_day}/{target_month}/{yr}",
                        "Original Dates Lifted From (पिछले महीने की किस तारीख से उठाया)": ", ".join(matched_dates[:3]) # Top 3 Matches
                    })
                else:
                    origin_results.append({
                        "Year": yr,
                        "Target Date": f"{target_day}/{target_month}/{yr}",
                        "Original Dates Lifted From (पिछले महीने की किस तारीख से उठाया)": "कोई डायरेक्ट/फैमिली मैच नहीं मिला"
                    })
        
        if origin_results:
            st.dataframe(pd.DataFrame(origin_results), use_container_width=True)
            
