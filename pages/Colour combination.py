import pandas as pd
import numpy as np

# 1. आपकी 10 मुख्य फैमिली कॉम्बिनेशन
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

def get_haruf(num_str):
    if not num_str or len(num_str) < 2:
        return None, None
    return num_str[0], num_str[1] # Inside (Ander), Outside (Bahar)

def run_full_pattern_analysis(csv_file, target_day=7, target_month=10, target_year=2025):
    df = pd.read_csv(csv_file)
    df['DATE_DT'] = pd.to_datetime(df['DATE'], format='%d/%m/%Y', errors='coerce')
    df = df.dropna(subset=['DATE_DT'])

    print(f"================================================================")
    print(f"  मास्टर पैटर्न एनालिसिस: तारीख {target_day}/{target_month} (13-14 साल डेटा)")
    print(f"================================================================\n")

    # -------------------------------------------------------------
    # PATTERN 1: Same Date Across All Years (2013 - 2026)
    # -------------------------------------------------------------
    print(f"--- [पैटर्न 1] सेम डेट ({target_day}/{target_month}) ईयर-वाइज़ रिकॉर्ड ---")
    same_date_df = df[(df['DATE_DT'].dt.day == target_day) & (df['DATE_DT'].dt.month == target_month)].sort_values('DATE_DT')
    
    for _, row in same_date_df.iterrows():
        yr = row['DATE_DT'].year
        frbd = clean_num(row['FRBD'])
        gzbd = clean_num(row['GZBD'])
        gali = clean_num(row['GALI'])
        dswr = clean_num(row['DSWR'])
        
        print(f"साल {yr} | FB: {frbd or 'XX'} ({get_family(frbd)}) | GB: {gzbd or 'XX'} ({get_family(gzbd)}) | GL: {gali or 'XX'} ({get_family(gali)}) | DS: {dswr or 'XX'} ({get_family(dswr)})")

    # -------------------------------------------------------------
    # PATTERN 2: 3-Month Block Analysis (Aug -> Sep -> Oct)
    # -------------------------------------------------------------
    print(f"\n--- [पैटर्न 2] 3-मंथ ब्लॉक (पिछले 2 महीने + चालू महीना) सेम डेट ---")
    months_block = [target_month-2 if target_month>2 else target_month+10, 
                    target_month-1 if target_month>1 else 12, 
                    target_month]
    
    for yr in range(2019, target_year + 1):
        print(f"\n>> वर्ष {yr} का 3-मंथ पैटर्न ({target_day} तारीख):")
        for m in months_block:
            m_yr = yr if m <= target_month else yr - 1
            m_data = df[(df['DATE_DT'].dt.year == m_yr) & (df['DATE_DT'].dt.month == m) & (df['DATE_DT'].dt.day == target_day)]
            if not m_data.empty:
                r = m_data.iloc[0]
                fb, gb, gl, ds = clean_num(r['FRBD']), clean_num(r['GZBD']), clean_num(r['GALI']), clean_num(r['DSWR'])
                print(f"  महीना {m}/{m_yr} | FB: {fb or 'XX'} ({get_family(fb)}) | GB: {gb or 'XX'} ({get_family(gb)}) | GL: {gl or 'XX'} ({get_family(gl)}) | DS: {ds or 'XX'} ({get_family(ds)})")

    # -------------------------------------------------------------
    # PATTERN 3: Cross-Month Date Lift (पिछले महीने की 20-30 तारीख से जंप)
    # -------------------------------------------------------------
    print(f"\n--- [पैटर्न 3] पिछले महीने से नंबर/फैमिली लिफ्ट का इतिहास ---")
    prev_m = target_month - 1 if target_month > 1 else 12
    
    for yr in range(2021, target_year + 1):
        prev_m_yr = yr if target_month > 1 else yr - 1
        # पिछले महीने की 20 से 30 तारीख
        p_data = df[(df['DATE_DT'].dt.year == prev_m_yr) & (df['DATE_DT'].dt.month == prev_m) & (df['DATE_DT'].dt.day.between(22, 28))]
        # चालू महीने की target_day
        c_data = df[(df['DATE_DT'].dt.year == yr) & (df['DATE_DT'].dt.month == target_month) & (df['DATE_DT'].dt.day == target_day)]
        
        if not c_data.empty and not p_data.empty:
            c_row = c_data.iloc[0]
            c_nums = [clean_num(c_row['FRBD']), clean_num(c_row['GZBD']), clean_num(c_row['GALI']), clean_num(c_row['DSWR'])]
            c_nums = [n for n in c_nums if n]
            
            for _, p_row in p_data.iterrows():
                p_day = p_row['DATE_DT'].day
                p_nums = [clean_num(p_row['FRBD']), clean_num(p_row['GZBD']), clean_num(p_row['GALI']), clean_num(p_row['DSWR'])]
                p_nums = [n for n in p_nums if n]
                
                # चेक फैमिली या नंबर मैच
                for cn in c_nums:
                    for pn in p_nums:
                        if cn == pn:
                            print(f"  साल {yr}: पिछले महीने {prev_m} की {p_day} तारीख का सिंगल नंबर {pn} -> {target_month} की {target_day} तारीख को रिपीट हुआ!")
                        elif get_family(cn) == get_family(pn) and get_family(cn) != "Other":
                            print(f"  साल {yr}: पिछले महीने {prev_m} की {p_day} तारीख से {get_family(cn)} फैमिली का नंबर खिसका ({pn} -> {cn})")

# कोड रन करने का तरीका:
# run_full_pattern_analysis("06_10_2026 result  (1).csv", target_day=7, target_month=10, target_year=2025)
