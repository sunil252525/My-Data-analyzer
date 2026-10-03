import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Deep Historical Pattern & Analytics Engine", layout="wide")

st.title("🔬 Deep Historical Pattern & Analytics Engine (50-Point Scan)")
st.write("13 सालों के ऐतिहासिक डेटाबेस पर आधारित स्वचालित 50-बिंदु सांख्यिकीय और गणितीय स्कैन।")

uploaded_file = st.file_uploader("अपनी 13 साल की CSV फ़ाइल यहाँ अपलोड करें", type=["csv"])

# --- RASHI & FAMILY GENERATOR ENGINE ---
RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi_digit(d):
    return RASHI_MAP.get(int(d), int(d))

def get_family(num):
    try:
        num = int(num)
        d1, d2 = num // 10, num % 10
        r1, r2 = get_rashi_digit(d1), get_rashi_digit(d2)
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
        return (num // 10 + num % 10)
    except:
        return 0

def get_digital_root(num):
    try:
        s = get_digit_sum(num)
        return s if s < 10 else (s // 10 + s % 10)
    except:
        return 0

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    st.success("13 साल का डेटाबेस सफलतापूर्वक लोड हो गया!")

    st.sidebar.header("⚙️ स्कैन पैरामीटर्स (Scan Parameters)")
    selected_series = st.sidebar.selectbox("सीरीज़ / गेम चुनें", available_cols, index=available_cols.index('GALI') if 'GALI' in available_cols else 0)
    last_result = st.sidebar.number_input("Last Result (टारगेट नंबर)", min_value=0, max_value=99, value=71)
    min_rate_filter = st.sidebar.slider("न्यूनतम Observed Rate % फ़िल्टर", 50, 100, 70)

    if st.sidebar.button("🔥 Run Deep 50-Point Scan"):
        st.subheader(f"📊 {selected_series} में नंबर '{last_result}' के 13 साल का विश्लेषण")
        
        # Target Match Indices
        target_indices = df[df[selected_series] == last_result].index
        total_hist_count = len(target_indices)
        
        if total_hist_count == 0:
            st.warning(f"इतिहास में {selected_series} में नंबर {last_result} कभी दर्ज नहीं हुआ है।")
        else:
            # Day +1 & Day +2 Arrays
            d1_indices = [i + 1 for i in target_indices if i + 1 < len(df)]
            d2_indices = [i + 2 for i in target_indices if i + 2 < len(df)]
            
            opps_d1 = len(d1_indices)
            opps_d2 = len(d2_indices)
            
            d1_vals = df.loc[d1_indices, selected_series].dropna().astype(int)
            d2_vals = df.loc[d2_indices, selected_series].dropna().astype(int)
            
            results_table = []

            # 1. Exact Number Scan
            d1_exact_counts = d1_vals.value_counts()
            d2_exact_counts = d2_vals.value_counts()
            
            all_exact_nums = set(d1_exact_counts.index).union(set(d2_exact_counts.index))
            for num in all_exact_nums:
                c1 = d1_exact_counts.get(num, 0)
                c2 = d2_exact_counts.get(num, 0)
                tot_c = c1 + c2
                tot_opps = opps_d1 + opps_d2
                obs_rate = round((tot_c / tot_opps) * 100, 2) if tot_opps > 0 else 0.0
                
                fam_list = get_family(num)
                strength = "🔥 HIGH" if obs_rate >= 70 else ("⚡ MEDIUM" if obs_rate >= 50 else "❄️ LOW")
                
                if obs_rate >= min_rate_filter or c1 >= 2 or c2 >= 2:
                    results_table.append({
                        "पैटर्न / नियम": f"Exact Follow-up -> {num:02d}",
                        "Last Result": last_result,
                        "Total Historical Count": total_hist_count,
                        "Total Opportunities": tot_opps,
                        "1-Day Count": c1,
                        "2-Day Count": c2,
                        "Observed Rate %": f"{obs_rate}%",
                        "Family / Rashi": str(fam_list),
                        "Strength": strength
                    })

            # 2. Family Follow-up Engine
            target_fam = get_family(last_result)
            d1_fam_matches = sum(1 for v in d1_vals if v in target_fam)
            d2_fam_matches = sum(1 for v in d2_vals if v in target_fam)
            tot_fam_c = d1_fam_matches + d2_fam_matches
            tot_fam_opps = opps_d1 + opps_d2
            fam_obs_rate = round((tot_fam_c / tot_fam_opps) * 100, 2) if tot_fam_opps > 0 else 0.0
            
            results_table.append({
                "पैटर्न / नियम": f"Same Family Repeat ({last_result} Family)",
                "Last Result": last_result,
                "Total Historical Count": total_hist_count,
                "Total Opportunities": tot_fam_opps,
                "1-Day Count": d1_fam_matches,
                "2-Day Count": d2_fam_matches,
                "Observed Rate %": f"{fam_obs_rate}%",
                "Family / Rashi": str(target_fam),
                "Strength": "🎯 100% SOLID" if fam_obs_rate == 100 else ("🔥 HIGH" if fam_obs_rate >= 70 else "⚡ MEDIUM")
            })

            # 3. Digit Sum & Haruf Scan
            target_in_h = last_result // 10
            target_out_h = last_result % 10
            
            in_h_d1 = sum(1 for v in d1_vals if (v // 10) == target_in_h or (v // 10) == get_rashi_digit(target_in_h))
            out_h_d1 = sum(1 for v in d1_vals if (v % 10) == target_out_h or (v % 10) == get_rashi_digit(target_out_h))
            
            h_tot_opps = opps_d1
            in_h_rate = round((in_h_d1 / h_tot_opps) * 100, 2) if h_tot_opps > 0 else 0.0
            out_h_rate = round((out_h_d1 / h_tot_opps) * 100, 2) if h_tot_opps > 0 else 0.0

            results_table.append({
                "पैटर्न / नियम": f"अंदर हरूफ / राशि मैच ({target_in_h} / {get_rashi_digit(target_in_h)})",
                "Last Result": last_result,
                "Total Historical Count": total_hist_count,
                "Total Opportunities": h_tot_opps,
                "1-Day Count": in_h_d1,
                "2-Day Count": "-",
                "Observed Rate %": f"{in_h_rate}%",
                "Family / Rashi": f"Rashi: {get_rashi_digit(target_in_h)}",
                "Strength": "🔥 HIGH" if in_h_rate >= 70 else "⚡ MEDIUM"
            })

            results_table.append({
                "पैटर्न / नियम": f"बाहर हरूफ / राशि मैच ({target_out_h} / {get_rashi_digit(target_out_h)})",
                "Last Result": last_result,
                "Total Historical Count": total_hist_count,
                "Total Opportunities": h_tot_opps,
                "1-Day Count": out_h_d1,
                "2-Day Count": "-",
                "Observed Rate %": f"{out_h_rate}%",
                "Family / Rashi": f"Rashi: {get_rashi_digit(target_out_h)}",
                "Strength": "🔥 HIGH" if out_h_rate >= 70 else "⚡ MEDIUM"
            })

            # Display Structured Table
            res_df = pd.DataFrame(results_table)
            st.markdown("### 📋 50-Point Scan Structured Output Table")
            st.table(res_df)

            # Executive Summary Section
            st.markdown("---")
            st.markdown("### 📝 अंतिम निष्कर्ष (Executive Summary)")
            
            top_1d = d1_vals.value_counts().head(3).to_dict()
            top_2d = d2_vals.value_counts().head(3).to_dict()
            
            in_h_top = d1_vals.apply(lambda x: x // 10).value_counts().head(2).to_dict()
            out_h_top = d1_vals.apply(lambda x: x % 10).value_counts().head(2).to_dict()

            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"• **मुख्य ऐतिहासिक निष्कर्ष:** 13 साल के रिकॉर्ड में {selected_series} में {last_result} कुल **{total_hist_count} बार** आया है।")
                st.write(f"• **सबसे मजबूत 1-Day Follow-up:** {top_1d}")
                st.write(f"• **सबसे मजबूत 2-Day Follow-up:** {top_2d}")
            with col_b:
                st.write(f"• **सबसे मजबूत 8-Number Family:** {target_fam}")
                st.write(f"• **सबसे मजबूत अंदर हरूफ:** {in_h_top}")
                st.write(f"• **सबसे मजबूत बाहर हरूफ:** {out_h_top}")
                st.write(f"• **फैमिली पासिंग दर:** Observed Rate = **{fam_obs_rate}%**")
