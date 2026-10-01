import streamlit as st
import pandas as pd
import numpy as np

# Page Layout Configuration
st.set_page_config(page_title="Deep Historical Pattern & Analytics Engine", layout="wide")

st.title("🔬 Deep Historical Pattern & Analytics Engine (Multi-Game Dashboard)")
st.write("13 सालों के ऐतिहासिक डेटाबेस पर आधारित स्वचालित सांख्यिकीय और गणितीय स्कैन।")

# ----------------------------------------------------
# 1. Main Page CSV File Uploader
# ----------------------------------------------------
uploaded_file = st.file_uploader("अपनी CSV फ़ाइल यहाँ अपलोड करें", type=["csv"])

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

    st.success("✅ डेटाबेस सफलतापूर्वक लोड हो गया!")

    # ----------------------------------------------------
    # 2. Scan Parameters (Defaulted to 100%)
    # ----------------------------------------------------
    st.markdown("---")
    st.subheader("⚙️ स्कैन पैरामीटर्स (Scan Parameters)")
    
    col1, col2 = st.columns([2, 2])
    
    with col1:
        # Slider value automatically set to 100
        min_rate_filter = st.slider("न्यूनतम Observed Rate % फ़िल्टर", 10, 100, 100)
        
    with col2:
        st.info("💡 सिस्टम हर गेम का सबसे आख़िरी रिजल्ट स्वतः (Automatically) फ़ेच करेगा।")

    run_scan = st.button("🔥 Run Multi-Game Auto Scan (एक साथ सभी गेम देखें)", use_container_width=True)

    if run_scan:
        st.markdown("---")
        
        # Streamlit Tabs for All Games on One Page
        tabs = st.tabs([f"🎯 {col}" for col in available_cols])
        
        for idx, col in enumerate(available_cols):
            with tabs[idx]:
                valid_series = df[col].dropna().astype(int)
                
                if valid_series.empty:
                    st.warning(f"{col} में कोई वैध डेटा नहीं है।")
                    continue
                
                # Auto-detect last result for this specific game
                last_result = valid_series.iloc[-1]
                
                t_idx = df[df[col] == last_result].index
                total_hist_count = len(t_idx)
                
                d1_idx = [i + 1 for i in t_idx if i + 1 < len(df)]
                d2_idx = [i + 2 for i in t_idx if i + 2 < len(df)]
                
                d1_vals_list = df.loc[d1_idx, col].dropna().astype(int).tolist()
                d2_vals_list = df.loc[d2_idx, col].dropna().astype(int).tolist()

                if total_hist_count == 0:
                    st.warning(f"इतिहास में {col} में नंबर {last_result:02d} दर्ज नहीं है।")
                else:
                    d1_vals = pd.Series(d1_vals_list)
                    d2_vals = pd.Series(d2_vals_list)
                    
                    opps_d1 = len(d1_vals)
                    opps_d2 = len(d2_vals)
                    
                    top_1d = d1_vals.value_counts().head(5)
                    top_2d = d2_vals.value_counts().head(5)
                    
                    target_fam = get_family(last_result)
                    fam_m1 = sum(1 for v in d1_vals_list if v in target_fam)
                    fam_m2 = sum(1 for v in d2_vals_list if v in target_fam)
                    fam_obs_rate = round(((fam_m1 + fam_m2) / (opps_d1 + opps_d2)) * 100, 2) if (opps_d1 + opps_d2) > 0 else 0.0
                    
                    # Top 2 Inside & Outside Harufs
                    in_h_top2 = d1_vals.apply(lambda x: x // 10).value_counts().head(2)
                    out_h_top2 = d1_vals.apply(lambda x: x % 10).value_counts().head(2)

                    in_harufs = list(in_h_top2.index)
                    out_harufs = list(out_h_top2.index)

                    # 2x2 Direct Crossing & 4x4 Rashi Crossing
                    crossed_pairs_2x2 = [f"{i}{o}" for i in in_harufs for o in out_harufs]
                    in_harufs_with_rashi = list(dict.fromkeys([h for h in in_harufs] + [get_rashi_digit(h) for h in in_harufs]))
                    out_harufs_with_rashi = list(dict.fromkeys([h for h in out_harufs] + [get_rashi_digit(h) for h in out_harufs]))
                    crossed_pairs_4x4 = [f"{i}{o}" for i in in_harufs_with_rashi for o in out_harufs_with_rashi]

                    # Executive Summary for Game
                    st.subheader(f"📌 {col} का विश्लेषण (Last Result: {last_result:02d})")
                    st.write(f"• **ऐतिहासिक रिकॉर्ड:** **{last_result:02d}** कुल **{total_hist_count} बार** आया है।")
                    st.write(f"• **1-Day Follow-up:** {top_1d.to_dict()}")
                    st.write(f"• **2-Day Follow-up:** {top_2d.to_dict()}")
                    st.write(f"• **8-Number Family:** {target_fam}")
                    st.write(f"• **अंदर हरूफ:** {in_harufs} | **बाहर हरूफ:** {out_harufs}")
                    st.write(f"• **फैमिली पासिंग दर:** Observed Rate = **{fam_obs_rate}%**")
                    
                    st.markdown("---")
                    
                    # Copy Boxes
                    c_box1, c_box2 = st.columns(2)
                    
                    with c_box1:
                        st.markdown("**📋 1-Day Follow-up Numbers:**")
                        st.code(", ".join([f"{num:02d}" for num in top_1d.index]), language="text")
                        
                        st.markdown("**🎯 हरूफ 2x2 क्रॉसिंग नंबर (4 जोड़ी):**")
                        st.code(", ".join(crossed_pairs_2x2), language="text")

                    with c_box2:
                        st.markdown("**📋 2-Day Follow-up Numbers:**")
                        st.code(", ".join([f"{num:02d}" for num in top_2d.index]), language="text")
                        
                        st.markdown("**🔥 राशि मिलाकर हरूफ क्रॉसिंग नंबर (16 जोड़ी):**")
                        st.code(", ".join(crossed_pairs_4x4), language="text")

                    # Filtered Output Table (Minimum Rate Filtered)
                    st.markdown("#### 📊 50-Point Scan Table Filtered")
                    results_table = []
                    all_exact_nums = set(top_1d.index).union(set(top_2d.index))
                    
                    for num in all_exact_nums:
                        c1 = (d1_vals == num).sum()
                        c2 = (d2_vals == num).sum()
                        tot_c = c1 + c2
                        tot_opps = opps_d1 + opps_d2
                        obs_rate = round((tot_c / tot_opps) * 100, 2) if tot_opps > 0 else 0.0
                        
                        if obs_rate >= min_rate_filter:
                            results_table.append({
                                "पैटर्न / नियम": f"Exact Follow-up -> {num:02d}",
                                "Last Result": f"{last_result:02d}",
                                "Total Historical Count": total_hist_count,
                                "Observed Rate %": f"{obs_rate}%",
                                "Family / Rashi": str(get_family(num)),
                                "Strength": "🔥 HIGH" if obs_rate >= 10 else "⚡ MEDIUM"
                            })

                    if fam_obs_rate >= min_rate_filter:
                        results_table.append({
                            "पैटर्न / नियम": f"Same Family Repeat ({last_result:02d})",
                            "Last Result": f"{last_result:02d}",
                            "Total Historical Count": total_hist_count,
                            "Observed Rate %": f"{fam_obs_rate}%",
                            "Family / Rashi": str(target_fam),
                            "Strength": "🎯 100% SOLID" if fam_obs_rate == 100 else "🔥 HIGH"
                        })

                    if results_table:
                        st.table(pd.DataFrame(results_table))
                    else:
                        st.info(f"Observed Rate >= {min_rate_filter}% का कोई रिकॉर्ड नहीं मिला। फ़िल्टर कम करके देखें।")
                        
