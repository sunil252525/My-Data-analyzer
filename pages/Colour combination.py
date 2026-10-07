Import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Auto Pattern Search Engine", layout="wide")

st.title("🎯 Auto 13-Year Pattern & Combination Analyzer")

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

    # Session State Initialization for Controls
    if 'target_day' not in st.session_state:
        st.session_state.target_day = default_day
    if 'target_month' not in st.session_state:
        st.session_state.target_month = default_month
    if 'day_margin' not in st.session_state:
        st.session_state.day_margin = 1

    st.info(f"📌 **Auto-Detected Latest Date:** {default_day}/{default_month}/{default_year}")

    # -------------------------------------------------------------
    # 4. PLUS / MINUS BUTTON CONTROLS (NO SLIDERS)
    # -------------------------------------------------------------
    st.sidebar.header("⚙️ Date & Margin Controls (+ / -)")

    # Day Control
    st.sidebar.subheader("📅 Date Adjustment (Tarikh)")
    col_d1, col_d2, col_d3 = st.sidebar.columns([1, 2, 1])
    if col_d1.button("➖ Day"):
        if st.session_state.target_day > 1:
            st.session_state.target_day -= 1
    col_d2.markdown(f"<h3 style='text-align: center; margin:0;'>{st.session_state.target_day}</h3>", unsafe_allow_html=True)
    if col_d3.button("➕ Day"):
        if st.session_state.target_day < 31:
            st.session_state.target_day += 1

    # Month Control
    st.sidebar.subheader("🗓️ Month Adjustment (Mahina)")
    col_m1, col_m2, col_m3 = st.sidebar.columns([1, 2, 1])
    if col_m1.button("➖ Month"):
        if st.session_state.target_month > 1:
            st.session_state.target_month -= 1
    col_m2.markdown(f"<h3 style='text-align: center; margin:0;'>{st.session_state.target_month}</h3>", unsafe_allow_html=True)
    if col_m3.button("➕ Month"):
        if st.session_state.target_month < 12:
            st.session_state.target_month += 1

    # Margin Range Control
    st.sidebar.subheader("↔️ Margin Range (+/- Days)")
    col_r1, col_r2, col_r3 = st.sidebar.columns([1, 2, 1])
    if col_r1.button("➖ Margin"):
        if st.session_state.day_margin > 0:
            st.session_state.day_margin -= 1
    col_r2.markdown(f"<h3 style='text-align: center; margin:0;'>+/- {st.session_state.day_margin}</h3>", unsafe_allow_html=True)
    if col_r3.button("➕ Margin"):
        if st.session_state.day_margin < 5:
            st.session_state.day_margin += 1

    # Target Year Dropdown
    available_years = sorted(df['DATE_DT'].dt.year.unique(), reverse=True)
    target_year = st.sidebar.selectbox("Select Target Year (Saal)", available_years, index=0)

    target_day = st.session_state.target_day
    target_month = st.session_state.target_month
    day_margin = st.session_state.day_margin

    # Calculate Range of Days
    target_days_range = [d for d in range(target_day - day_margin, target_day + day_margin + 1) if 1 <= d <= 31]

    # 5. Family Groups
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
        except Exception:
            return str(val).strip().zfill(2)

    def get_family(num_str):
        if not num_str:
            return "N/A"
        for fam_name, members in FAMILY_GROUPS.items():
            if num_str in members:
                return fam_name
        return "Other"

    def get_haruf(num_str):
        if not num_str or len(num_str) < 2:
            return None, None
        return num_str[0], num_str[1]

    # UI Tabs
    tab1, tab2, tab3 = st.tabs(["1️⃣ Same Date (+/- Range)", "2️⃣ 3-Month Block Sequence", "3️⃣ Cross-Month Lift"])

    # --- TAB 1: SAME DATE WITH PLUS/MINUS MARGIN ---
    with tab1:
        st.subheader(f"📅 Pattern 1: Dates {target_days_range} / Month {target_month} Across All Years (+/- {day_margin} Days)")
        
        same_date_df = df[(df['DATE_DT'].dt.day.isin(target_days_range)) & (df['DATE_DT'].dt.month == target_month)].sort_values('DATE_DT', ascending=False)
        
        table_data = []
        all_families = []
        inside_harufs = []
        outside_harufs = []

        for _, row in same_date_df.iterrows():
            yr = row['DATE_DT'].year
            day_val = row['DATE_DT'].day
            fb = clean_num(row['FRBD'])
            gb = clean_num(row['GZBD'])
            gl = clean_num(row['GALI'])
            ds = clean_num(row['DSWR'])
            
            for n in [fb, gb, gl, ds]:
                if n:
                    fam = get_family(n)
                    if fam != "Other":
                        all_families.append(fam)
                    h_in, h_out = get_haruf(n)
                    if h_in:
                        inside_harufs.append(h_in)
                    if h_out:
                        outside_harufs.append(h_out)

            table_data.append({
                "Year": yr,
                "Date": f"{day_val}/{target_month}/{yr}",
                "FRBD": f"{fb or 'XX'} ({get_family(fb)})",
                "GZBD": f"{gb or 'XX'} ({get_family(gb)})",
                "GALI": f"{gl or 'XX'} ({get_family(gl)})",
                "DSWR": f"{ds or 'XX'} ({get_family(ds)})"
            })

        st.markdown("### 📊 Auto-Pattern Detection Insights")
        col1, col2, col3 = st.columns(3)
        
        if all_families:
            top_fam = pd.Series(all_families).mode().tolist()
            col1.success(f"🔥 **Top Recurring Family:** {', '.join(top_fam)}")
        
        if inside_harufs:
            top_in = pd.Series(inside_harufs).mode().tolist()
            col2.info(f"🎯 **Top Inside Haruf:** {', '.join(top_in)}")
            
        if outside_harufs:
            top_out = pd.Series(outside_harufs).mode().tolist()
            col3.info(f"🎯 **Top Outside Haruf:** {', '.join(top_out)}")

        st.dataframe(pd.DataFrame(table_data), use_container_width=True)

    # --- TAB 2: 3-MONTH BLOCK SEQUENCE ---
    with tab2:
        st.subheader("🗓️ Pattern 2: 3-Month Block Sequence Analysis")
        m1 = target_month - 2 if target_month > 2 else target_month + 10
        m2 = target_month - 1 if target_month > 1 else 12
        m3 = target_month
        
        st.write(f"Sequence: **Month {m1} ➡️ Month {m2} ➡️ Month {m3}** | Dates: **{target_days_range}**")
        
        block_data = []
        for yr in sorted(df['DATE_DT'].dt.year.unique(), reverse=True):
            if yr <= target_year:
                for m in [m1, m2, m3]:
                    m_yr = yr if m <= target_month else yr - 1
                    m_df = df[(df['DATE_DT'].dt.year == m_yr) & (df['DATE_DT'].dt.month == m) & (df['DATE_DT'].dt.day.isin(target_days_range))]
                    for _, r in m_df.iterrows():
                        fb = clean_num(r['FRBD'])
                        gb = clean_num(r['GZBD'])
                        gl = clean_num(r['GALI'])
                        ds = clean_num(r['DSWR'])
                        block_data.append({
                            "Year": m_yr,
                            "Month": m,
                            "Date": f"{r['DATE_DT'].day}/{m}/{m_yr}",
                            "FRBD": f"{fb or 'XX'} ({get_family(fb)})",
                            "GZBD": f"{gb or 'XX'} ({get_family(gb)})",
                            "GALI": f"{gl or 'XX'} ({get_family(gl)})",
                            "DSWR": f"{ds or 'XX'} ({get_family(ds)})"
                        })
        if block_data:
            st.dataframe(pd.DataFrame(block_data), use_container_width=True)

    # --- TAB 3: CROSS-MONTH LIFT ---
    with tab3:
        st.subheader("🔀 Pattern 3: Cross-Month Lift Analysis")
        prev_m = target_month - 1 if target_month > 1 else 12
        prev_m_yr = target_year if target_month > 1 else target_year - 1
        
        st.write(f"Target Dates: **{target_days_range}/{target_month}/{target_year}** vs **Month {prev_m}/{prev_m_yr} (Dates 20 to 30)**")
        
        p_data = df[(df['DATE_DT'].dt.year == prev_m_yr) & (df['DATE_DT'].dt.month == prev_m) & (df['DATE_DT'].dt.day.between(20, 30))]
        c_data = df[(df['DATE_DT'].dt.year == target_year) & (df['DATE_DT'].dt.month == target_month) & (df['DATE_DT'].dt.day.isin(target_days_range))]
        
        p_table = []
        for _, p_row in p_data.iterrows():
            fb = clean_num(p_row['FRBD'])
            gb = clean_num(p_row['GZBD'])
            gl = clean_num(p_row['GALI'])
            ds = clean_num(p_row['DSWR'])
            p_table.append({
                "Date": p_row['DATE_DT'].strftime('%d/%m/%Y'),
                "FRBD": f"{fb or 'XX'} ({get_family(fb)})",
                "GZBD": f"{gb or 'XX'} ({get_family(gb)})",
                "GALI": f"{gl or 'XX'} ({get_family(gl)})",
                "DSWR": f"{ds or 'XX'} ({get_family(ds)})"
            })
        if p_table:
            st.dataframe(pd.DataFrame(p_table), use_container_width=True)

        if not c_data.empty:
            st.write("🔍 **Matching Results:**")
            matches = []
            for _, c_row in c_data.iterrows():
                c_day = c_row['DATE_DT'].day
                c_nums = { "FB": clean_num(c_row['FRBD']), "GB": clean_num(c_row['GZBD']), "GL": clean_num(c_row['GALI']), "DS": clean_num(c_row['DSWR']) }
                
                for _, p_row in p_data.iterrows():
                    p_day = p_row['DATE_DT'].day
                    p_nums = { "FB": clean_num(p_row['FRBD']), "GB": clean_num(p_row['GZBD']), "GL": clean_num(p_row['GALI']), "DS": clean_num(p_row['DSWR']) }
                    
                    for c_game, cn in c_nums.items():
                        for p_game, pn in p_nums.items():
                            if cn and pn:
                                if cn == pn:
                                    matches.append(f"🔥 **SINGLE MATCH**: Prev Month Day {p_day} ({p_game}: {pn}) ➡️ Target Day {c_day} ({c_game}: {cn})")
                                elif get_family(cn) == get_family(pn) and get_family(cn) != "Other":
                                    matches.append(f"✨ **FAMILY MATCH ({get_family(cn)})**: Prev Month Day {p_day} ({p_game}: {pn}) ➡️ Target Day {c_day} ({c_game}: {cn})")
            
            if matches:
                for m in matches:
                    st.success(m)
            else:
                st.warning("Koi direct ya family match nahi mila.")

        
