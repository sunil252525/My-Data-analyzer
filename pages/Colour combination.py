import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Auto Pattern Search Engine", layout="wide")

st.title("🎯 Auto 13-Year Pattern & Combination Analyzer")

@st.cache_data
def load_csv_data(file_source):
    df = pd.read_csv(file_source)
    df['DATE_DT'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y', errors='coerce')
    df = df.dropna(subset=['DATE_DT']).sort_values('DATE_DT')
    return df

# 2. Main Page File Upload
st.markdown("### 📁 **Upload Your Result CSV File**")
uploaded_file = st.file_uploader("Upload CSV File Here", type=["csv"], label_visibility="collapsed")

df = None

if uploaded_file is not None:
    try:
        df = load_csv_data(uploaded_file)
        st.success("✅ File Loaded Successfully!")
    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    try:
        df = load_csv_data("06_10_2026 result  (1).csv")
        st.info("ℹ️ Using default repository CSV file.")
    except Exception:
        st.warning("⚠️ Kripya ऊपर 'Upload CSV File' बटन से अपनी CSV फाइल अपलोड करें!")

if df is not None and not df.empty:

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
            return "XX"
        try:
            return str(int(float(val))).zfill(2)
        except Exception:
            return str(val).strip().zfill(2)

    def get_family(num_str):
        if not num_str or num_str == "XX":
            return "N/A"
        for fam_name, members in FAMILY_GROUPS.items():
            if num_str in members:
                return fam_name
        return "Other"

    def get_haruf(num_str):
        if not num_str or num_str == "XX" or len(num_str) < 2:
            return None, None
        return num_str[0], num_str[1]

    # Dynamically detect all game columns present in CSV
    possible_games = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    game_columns = [col for col in possible_games if col in df.columns]
    if not game_columns:
        game_columns = [col for col in df.columns if col not in ['DATE', 'DATE_DT', 'Unnamed: 0'] and not col.startswith('Unnamed')]

    # Auto Detect Latest Date
    valid_data_df = df.dropna(subset=game_columns, how='all')
    
    if not valid_data_df.empty:
        latest_row = valid_data_df.iloc[-1]
        default_day = int(latest_row['DATE_DT'].day)
        default_month = int(latest_row['DATE_DT'].month)
        default_year = int(latest_row['DATE_DT'].year)
    else:
        default_day, default_month, default_year = 6, 10, 2026

    st.markdown("---")

    # 4. RECENT RESULTS CARDS
    st.markdown("### 📦 **हाल ही के रिजल्ट्स (Last 5 Results):**")

    for g_col in game_columns:
        col_vals = df[g_col].dropna().astype(str).str.strip()
        cleaned_vals = [clean_num(v) for v in col_vals if v.lower() not in ['nan', 'xx', '']]
        if cleaned_vals:
            last_5 = cleaned_vals[-5:]
            results_str = " - ".join(last_5)
            st.markdown(
                f"""
                <div style="
                    border: 1px solid #d0d0d0;
                    border-radius: 12px;
                    padding: 12px 20px;
                    margin-bottom: 10px;
                    text-align: center;
                    background-color: #ffffff;
                    box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
                    font-size: 17px;
                    font-weight: 600;
                    color: #222222;
                    letter-spacing: 0.5px;">
                    📌 <strong>{g_col}</strong> {results_str}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")

    # Session State Initialization
    if 'target_day' not in st.session_state:
        st.session_state.target_day = default_day
    if 'target_month' not in st.session_state:
        st.session_state.target_month = default_month
    if 'day_margin' not in st.session_state:
        st.session_state.day_margin = 1

    # 5. MAIN PAGE CONTROLS (DATE, MONTH, MARGIN & YEAR)
    st.markdown("### ⚙️ **Date & Pattern Controls (+ / -)**")

    c_day, c_month, c_margin, c_year = st.columns([2, 2, 2, 2])

    with c_day:
        st.markdown("**📅 Day (Tarikh)**")
        d1, d2, d3 = st.columns([1, 2, 1])
        if d1.button("➖", key="d_minus"):
            if st.session_state.target_day > 1:
                st.session_state.target_day -= 1
        d2.markdown(f"<h3 style='text-align: center; margin:0;'>{st.session_state.target_day}</h3>", unsafe_allow_html=True)
        if d3.button("➕", key="d_plus"):
            if st.session_state.target_day < 31:
                st.session_state.target_day += 1

    with c_month:
        st.markdown("**🗓️ Month (Mahina)**")
        m1, m2, m3 = st.columns([1, 2, 1])
        if m1.button("➖", key="m_minus"):
            if st.session_state.target_month > 1:
                st.session_state.target_month -= 1
        m2.markdown(f"<h3 style='text-align: center; margin:0;'>{st.session_state.target_month}</h3>", unsafe_allow_html=True)
        if m3.button("➕", key="m_plus"):
            if st.session_state.target_month < 12:
                st.session_state.target_month += 1

    with c_margin:
        st.markdown("**↔️ Margin Range**")
        r1, r2, r3 = st.columns([1, 2, 1])
        if r1.button("➖", key="r_minus"):
            if st.session_state.day_margin > 0:
                st.session_state.day_margin -= 1
        r2.markdown(f"<h3 style='text-align: center; margin:0;'>+/- {st.session_state.day_margin}</h3>", unsafe_allow_html=True)
        if r3.button("➕", key="r_plus"):
            if st.session_state.day_margin < 5:
                st.session_state.day_margin += 1

    with c_year:
        st.markdown("**📆 Target Year**")
        available_years = sorted(df['DATE_DT'].dt.year.unique(), reverse=True)
        target_year = st.selectbox("Year", available_years, index=0, label_visibility="collapsed")

    target_day = st.session_state.target_day
    target_month = st.session_state.target_month
    day_margin = st.session_state.day_margin

    # Calculate Range of Days
    target_days_range = [d for d in range(target_day - day_margin, target_day + day_margin + 1) if 1 <= d <= 31]

    st.markdown("---")

    # 6. UI Tabs for Patterns Analysis
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
            
            row_dict = {"Year": yr, "Date": f"{day_val}/{target_month}/{yr}"}
            
            for g_col in game_columns:
                g_val = clean_num(row.get(g_col))
                row_dict[g_col] = f"{g_val} ({get_family(g_val)})"
                
                if g_val != "XX":
                    fam = get_family(g_val)
                    if fam not in ["N/A", "Other"]:
                        all_families.append(fam)
                    h_in, h_out = get_haruf(g_val)
                    if h_in:
                        inside_harufs.append(h_in)
                    if h_out:
                        outside_harufs.append(h_out)

            table_data.append(row_dict)

        st.markdown("### 📊 Auto-Pattern Detection Insights (Selected Range)")
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

        # --- DAY-BY-DAY TOP RECURRING FAMILY CARDS (-7 Days to +4 Days) ---
        st.markdown("---")
        st.markdown("### 🗓️ **Day-by-Day Top Recurring Family (-7 Days to +4 Days)**")
        st.caption(f"महीना {target_month} के लिए हर तारीख की Top Recurring Family अलग-अलग (सभी वर्षों का डेटा):")

        ext_start_day = max(1, target_day - 7)
        ext_end_day = min(31, target_day + 4)

        for single_day in range(ext_start_day, ext_end_day + 1):
            single_day_df = df[(df['DATE_DT'].dt.day == single_day) & (df['DATE_DT'].dt.month == target_month)]
            day_fams = []
            
            for _, r in single_day_df.iterrows():
                for g_c in game_columns:  # Correctly checking ALL game columns
                    val = clean_num(r.get(g_c))
                    if val != "XX":
                        f_name = get_family(val)
                        if f_name not in ["N/A", "Other"]:
                            day_fams.append(f_name)
            
            if day_fams:
                top_day_fam = ", ".join(pd.Series(day_fams).mode().tolist())
            else:
                top_day_fam = "N/A"

            # Tag for Current/Target Day
            tag_label = "(Target Day)" if single_day == target_day else ("(Past Day)" if single_day < target_day else "(Next Day)")
            bg_color = "#e8f5e9" if single_day == target_day else "#ffffff"

            st.markdown(
                f"""
                <div style="
                    border: 1px solid #c0c0c0;
                    border-radius: 10px;
                    padding: 10px 18px;
                    margin-bottom: 8px;
                    background-color: {bg_color};
                    box-shadow: 0px 1px 3px rgba(0,0,0,0.05);
                    font-size: 16px;
                    font-weight: 600;
                    color: #111111;">
                    📅 <strong>तारीख {single_day}/{target_month} {tag_label}:</strong> &nbsp;&nbsp; 🔥 Top Recurring Family: <span style="color: #0d6efd;">{top_day_fam}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

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
                        b_row = {"Year": m_yr, "Month": m, "Date": f"{r['DATE_DT'].day}/{m}/{m_yr}"}
                        for g_col in game_columns:
                            b_val = clean_num(r.get(g_col))
                            b_row[g_col] = f"{b_val} ({get_family(b_val)})"
                        block_data.append(b_row)
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
            p_dict = {"Date": p_row['DATE_DT'].strftime('%d/%m/%Y')}
            for g_col in game_columns:
                p_val = clean_num(p_row.get(g_col))
                p_dict[g_col] = f"{p_val} ({get_family(p_val)})"
            p_table.append(p_dict)
            
        if p_table:
            st.dataframe(pd.DataFrame(p_table), use_container_width=True)

        if not c_data.empty:
            st.write("🔍 **Matching Results:**")
            matches = []
            for _, c_row in c_data.iterrows():
                c_day = c_row['DATE_DT'].day
                c_nums = {g_c: clean_num(c_row.get(g_c)) for g_c in game_columns}
                
                for _, p_row in p_data.iterrows():
                    p_day = p_row['DATE_DT'].day
                    p_nums = {g_c: clean_num(p_row.get(g_c)) for g_c in game_columns}
                    
                    for c_game, cn in c_nums.items():
                        for p_game, pn in p_nums.items():
                            if cn != "XX" and pn != "XX":
                                if cn == pn:
                                    matches.append(f"🔥 **SINGLE MATCH**: Prev Month Day {p_day} ({p_game}: {pn}) ➡️ Target Day {c_day} ({c_game}: {cn})")
                                elif get_family(cn) == get_family(pn) and get_family(cn) != "Other":
                                    matches.append(f"✨ **FAMILY MATCH ({get_family(cn)})**: Prev Month Day {p_day} ({p_game}: {pn}) ➡️ Target Day {c_day} ({c_game}: {cn})")
            
            if matches:
                for m in matches:
                    st.success(m)
            else:
                st.warning("Koi direct ya family match nahi mila.")
            
