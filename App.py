import streamlit as st
import pandas as pd
import numpy as np

# Page Layout Configuration
st.set_page_config(page_title="Deep Historical Pattern & Analytics Engine", layout="wide")

st.title("🔬 Deep Historical Pattern & Analytics Engine (50-Point Scan)")
st.write("13 सालों के ऐतिहासिक डेटाबेस पर आधारित स्वचालित 50-बिंदु सांख्यिकीय और गणितीय स्कैन।")

# ----------------------------------------------------
# 1. Main Page CSV File Uploader
# ----------------------------------------------------
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

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    st.success("✅ 13 साल का डेटाबेस सफलतापूर्वक लोड हो गया!")

    # ----------------------------------------------------
    # 2. Scan Parameters Directly on Main Page
    # ----------------------------------------------------
    st.markdown("---")
    st.subheader("⚙️ स्कैन पैरामीटर्स (Scan Parameters)")
    
    col1, col2, col3 = st.columns([1.5, 1.5, 2])
    
    with col1:
        game_options = ["ALL GAMES (सभी गेम)"] + available_cols
        selected_series = st.selectbox("सीरीज़ / गेम चुनें", game_options, index=0)
        
    with col2:
        last_result = st.number_input("Last Result (टारगेट नंबर)", min_value=0, max_value=99, value=71)
        
    with col3:
        min_rate_filter = st.slider("न्यूनतम Observed Rate % फ़िल्टर", 10, 100, 50)

    run_scan = st.button("🔥 Run Deep 50-Point Scan", use_container_width=True)

    if run_scan:
        st.markdown("---")
        
        scan_cols = available_cols if selected_series == "ALL GAMES (सभी गेम)" else [selected_series]
        
        all_d1_vals = []
        all_d2_vals = []
        total_hist_count = 0
        
        for col in scan_cols:
            t_idx = df[df[col] == last_result].index
            total_hist_count += len(t_idx)
            
            d1_idx = [i + 1 for i in t_idx if i + 1 < len(df)]
            d2_idx = [i + 2 for i in t_idx if i + 2 < len(df)]
            
            all_d1_vals.extend(df.loc[d1_idx, col].dropna().astype(int).tolist())
            all_d2_vals.extend(df.loc[d2_idx, col].dropna().astype(int).tolist())

        if total_hist_count == 0:
            st.warning(f"इतिहास में {selected_series} में नंबर {last_result:02d} कभी दर्ज नहीं हुआ है।")
        else:
            d1_series = pd.Series(all_d1_vals)
            d2_series = pd.Series(all_d2_vals)
            
            opps_d1 = len(all_d1_vals)
            opps_d2 = len(all_d2_vals)
            
            # Calculations
            top_1d = d1_series.value_counts().head(5)
            top_2d = d2_series.value_counts().head(5)
            
            target_fam = get_family(last_result)
            fam_m1 = sum(1 for v in all_d1_vals if v in target_fam)
            fam_m2 = sum(1 for v in all_d2_vals if v in target_fam)
            fam_obs_rate = round(((fam_m1 + fam_m2) / (opps_d1 + opps_d2)) * 100, 2) if (opps_d1 + opps_d2) > 0 else 0.0
            
            # Haruf extraction (Top 2 Inside and Top 2 Outside Harufs)
            in_h_top2 = d1_series.apply(lambda x: x // 10).value_counts().head(2)
            out_h_top2 = d1_series.apply(lambda x: x % 10).value_counts().head(2)

            in_harufs = list(in_h_top2.index)
            out_harufs = list(out_h_top2.index)

            # Creating 2x2 Direct Crossing Numbers
            crossed_pairs_2x2 = [f"{i}{o}" for i in in_harufs for o in out_harufs]

            # Creating 4x4 Crossing Numbers (including Rashis)
            in_harufs_with_rashi = list(dict.fromkeys([h for h in in_harufs] + [get_rashi_digit(h) for h in in_harufs]))
            out_harufs_with_rashi = list(dict.fromkeys([h for h in out_harufs] + [get_rashi_digit(h) for h in out_harufs]))
            crossed_pairs_4x4 = [f"{i}{o}" for i in in_harufs_with_rashi for o in out_harufs_with_rashi]

            # ----------------------------------------------------
            # EXECUTIVE SUMMARY
            # ----------------------------------------------------
            st.subheader("📝 अंतिम निष्कर्ष (Executive Summary)")
            st.write(f"• **मुख्य ऐतिहासिक निष्कर्ष:** 13 साल के रिकॉर्ड में **{selected_series}** में **{last_result:02d}** कुल **{total_hist_count} बार** आया है।")
            st.write(f"• **सबसे मजबूत 1-Day Follow-up:** {top_1d.to_dict()}")
            st.write(f"• **सबसे मजबूत 2-Day Follow-up:** {top_2d.to_dict()}")
            st.write(f"• **सबसे मजबूत 8-Number Family:** {target_fam}")
            st.write(f"• **टॉप 2 अंदर हरूफ:** {in_harufs}")
            st.write(f"• **टॉप 2 बाहर हरूफ:** {out_harufs}")
            st.write(f"• **फैमिली पासिंग दर:** Observed Rate = **{fam_obs_rate}%**")
            
            st.markdown("---")
            st.markdown("### 📋 डायरेक्ट कॉपी-पेस्ट सेक्शन्स (Direct Copy Box)")
            
            str_1d_copy = ", ".join([f"{num:02d}" for num in top_1d.index])
            str_2d_copy = ", ".join([f"{num:02d}" for num in top_2d.index])
            str_in_h_copy = ", ".join([str(h) for h in in_harufs])
            str_out_h_copy = ", ".join([str(h) for h in out_harufs])
            str_crossed_2x2 = ", ".join(crossed_pairs_2x2)
            str_crossed_4x4 = ", ".join(crossed_pairs_4x4)

            c_box1, c_box2 = st.columns(2)
            
            with c_box1:
                st.markdown("**📋 1-Day Follow-up Numbers:**")
                st.code(str_1d_copy, language="text")
                
                st.markdown("**📋 टॉप 2 अंदर हरूफ (Inside Haruf):**")
                st.code(str_in_h_copy, language="text")

                st.markdown("**🎯 हरूफ 2x2 क्रॉसिंग नंबर (4 जोड़ी):**")
                st.code(str_crossed_2x2, language="text")

            with c_box2:
                st.markdown("**📋 2-Day Follow-up Numbers:**")
                st.code(str_2d_copy, language="text")
                
                st.markdown("**📋 टॉप 2 बाहर हरूफ (Outside Haruf):**")
                st.code(str_out_h_copy, language="text")

                st.markdown("**🔥 राशि मिलाकर हरूफ क्रॉसिंग नंबर (16 जोड़ी):**")
                st.code(str_crossed_4x4, language="text")

            # ----------------------------------------------------
            # STRUCTURED OUTPUT TABLE
            # ----------------------------------------------------
            st.markdown("---")
            st.markdown("### 📊 50-Point Scan Structured Output Table")
            
            results_table = []
            all_exact_nums = set(top_1d.index).union(set(top_2d.index))
            for num in all_exact_nums:
                c1 = (d1_series == num).sum()
                c2 = (d2_series == num).sum()
                tot_c = c1 + c2
                tot_opps = opps_d1 + opps_d2
                obs_rate = round((tot_c / tot_opps) * 100, 2) if tot_opps > 0 else 0.0
                
                if obs_rate >= min_rate_filter or c1 >= 1 or c2 >= 1:
                    results_table.append({
                        "पैटर्न / नियम": f"Exact Follow-up -> {num:02d}",
                        "Last Result": f"{last_result:02d}",
                        "Total Historical Count": total_hist_count,
                        "Total Opportunities": tot_opps,
                        "1-Day Count": c1,
                        "2-Day Count": c2,
                        "Observed Rate %": f"{obs_rate}%",
                        "Family / Rashi": str(get_family(num)),
                        "Strength": "🔥 HIGH" if obs_rate >= 10 else "⚡ MEDIUM"
                    })

            results_table.append({
                "पैटर्न / नियम": f"Same Family Repeat ({last_result:02d} Family)",
                "Last Result": f"{last_result:02d}",
                "Total Historical Count": total_hist_count,
                "Total Opportunities": opps_d1 + opps_d2,
                "1-Day Count": fam_m1,
                "2-Day Count": fam_m2,
                "Observed Rate %": f"{fam_obs_rate}%",
                "Family / Rashi": str(target_fam),
                "Strength": "🎯 100% SOLID" if fam_obs_rate == 100 else ("🔥 HIGH" if fam_obs_rate >= 50 else "⚡ MEDIUM")
            })

            st.table(pd.DataFrame(results_table))
