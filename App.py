import streamlit as st
import pandas as pd
import numpy as np

# Page Layout Configuration
st.set_page_config(page_title="Deep Historical Pattern & Analytics Engine", layout="wide")

st.title("🔬 Deep Historical Pattern & Analytics Engine (Multi-Game Scan)")
st.write("13 सालों के ऐतिहासिक डेटाबेस पर आधारित स्वचालित सांख्यिकीय, हरूफ और ऑल-गेम पैटर्न स्कैन।")

# ----------------------------------------------------
# 1. Direct Main-Page File Uploading (No Sidebar Friction)
# ----------------------------------------------------
uploaded_file = st.file_uploader("📂 अपनी 13 साल की CSV फ़ाइल यहाँ अपलोड करें", type=["csv"])

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

    st.markdown("---")
    st.subheader("⚙️ स्कैन पैरामीटर्स (Scan Settings)")
    
    col_input1, col_input2 = st.columns([1, 2])
    with col_input1:
        last_result = st.number_input("Target Number (टारगेट नंबर):", min_value=0, max_value=99, value=71)
    with col_input2:
        st.write("🎯 **स्कैन मोड:** ऑटोमैटिक ऑल-गेम डीप स्कैन (`DB`, `SG`, `FRBD`, `GZBD`, `GALI`, `DSWR`)")

    if st.button("🔥 Run All-Game Deep 50-Point Scan", use_container_width=True):
        st.markdown("---")
        st.header(f"📊 टारगेट नंबर '{last_result:02d}' का सभी सीरीज़ में 13 साल का संयुक्त विश्लेषण")
        
        # Aggregation Stores Across All Games
        all_d1_vals = []
        all_d2_vals = []
        game_wise_summaries = {}
        total_global_occurrences = 0

        # Loop through every available game series
        for series in available_cols:
            target_indices = df[df[series] == last_result].index
            hist_count = len(target_indices)
            total_global_occurrences += hist_count
            
            if hist_count > 0:
                d1_idx = [i + 1 for i in target_indices if i + 1 < len(df)]
                d2_idx = [i + 2 for i in target_indices if i + 2 < len(df)]
                
                d1_vals = df.loc[d1_idx, series].dropna().astype(int).tolist()
                d2_vals = df.loc[d2_idx, series].dropna().astype(int).tolist()
                
                all_d1_vals.extend(d1_vals)
                all_d2_vals.extend(d2_vals)
                
                # Game Specific Family Matches
                target_fam = get_family(last_result)
                fam_m1 = sum(1 for v in d1_vals if v in target_fam)
                fam_m2 = sum(1 for v in d2_vals if v in target_fam)
                tot_fam = fam_m1 + fam_m2
                tot_opps = len(d1_vals) + len(d2_vals)
                fam_rate = round((tot_fam / tot_opps) * 100, 2) if tot_opps > 0 else 0.0
                
                game_wise_summaries[series] = {
                    "hist_count": hist_count,
                    "d1_series": pd.Series(d1_vals),
                    "d2_series": pd.Series(d2_vals),
                    "fam_rate": fam_rate,
                    "target_fam": target_fam
                }

        if total_global_occurrences == 0:
            st.warning(f"इतिहास में किसी भी गेम सीरीज़ में नंबर {last_result:02d} कभी दर्ज नहीं हुआ है।")
        else:
            # ----------------------------------------------------
            # EXECUTIVE SUMMARY (GLOBAL ALL-GAMES CONSOLIDATED)
            # ----------------------------------------------------
            st.subheader("📝 अंतिम निष्कर्ष (Executive Summary - All Games Combined)")
            
            s_d1_all = pd.Series(all_d1_vals)
            s_d2_all = pd.Series(all_d2_vals)
            
            tot_d1_opps = len(all_d1_vals)
            tot_d2_opps = len(all_d2_vals)

            top_1d_counts = s_d1_all.value_counts().head(5)
            top_2d_counts = s_d2_all.value_counts().head(5)
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("#### 🚀 सबसे मजबूत 1-Day Follow-up (All Games)")
                for num, count in top_1d_counts.items():
                    rate = round((count / tot_d1_opps) * 100, 2) if tot_d1_opps > 0 else 0
                    st.write(f"• **नंबर {num:02d}** -> आया **{count} बार** (Observed Rate: **{rate}%**)")
                    
            with col_b:
                st.markdown("#### ⚡ सबसे मजबूत 2-Day Follow-up (All Games)")
                for num, count in top_2d_counts.items():
                    rate = round((count / tot_d2_opps) * 100, 2) if tot_d2_opps > 0 else 0
                    st.write(f"• **नंबर {num:02d}** -> आया **{count} बार** (Observed Rate: **{rate}%**)")

            st.markdown("---")
            
            # ----------------------------------------------------
            # STEP-BY-STEP GAME-BY-GAME DETAILED BREAKDOWN
            # ----------------------------------------------------
            st.subheader("📌 स्टेप-बाय-स्टेप गेम-वाइज़ डीप रिपोर्ट (Game-Wise Step Breakdown)")
            
            for series_name, data in game_wise_summaries.items():
                with st.expander(f"🎮 {series_name} सीरीज़ - कुल ऐतिहासिक रिकॉर्ड्स: {data['hist_count']} बार", expanded=True):
                    c1, c2, c3 = st.columns(3)
                    
                    # Top 1-Day for this specific game
                    with c1:
                        st.markdown("**Top 1-Day Follow-up:**")
                        d1_top = data["d1_series"].value_counts().head(3)
                        d1_tot = len(data["d1_series"])
                        for num, count in d1_top.items():
                            p = round((count / d1_tot) * 100, 1) if d1_tot > 0 else 0
                            st.write(f"- `{num:02d}` : {count} बार ({p}%)")
                    
                    # Top 2-Day for this specific game
                    with c2:
                        st.markdown("**Top 2-Day Follow-up:**")
                        d2_top = data["d2_series"].value_counts().head(3)
                        d2_tot = len(data["d2_series"])
                        for num, count in d2_top.items():
                            p = round((count / d2_tot) * 100, 1) if d2_tot > 0 else 0
                            st.write(f"- `{num:02d}` : {count} बार ({p}%)")
                            
                    # Family Passing Rate
                    with c3:
                        st.markdown("**Family Match Rate:**")
                        st.write(f"• **{last_result:02d} Family:** `{data['target_fam']}`")
                        st.write(f"• **फैमिली पासिंग दर:** `{data['fam_rate']}%`")

            # ----------------------------------------------------
            # FULL STRUCTURED PATTERN TABLE
            # ----------------------------------------------------
            st.markdown("---")
            st.subheader("📋 50-Point Master Summary Table (All Games Combined)")
            
            summary_table = []
            for num, count in top_1d_counts.items():
                rate = round((count / tot_d1_opps) * 100, 2) if tot_d1_opps > 0 else 0
                summary_table.append({
                    "प्रकार": "1-Day Follow-up",
                    "Target Num": f"{last_result:02d}",
                    "Follow-up Number": f"{num:02d}",
                    "कुल आवृत्ति (Frequency)": f"{count} बार",
                    "Observed Rate %": f"{rate}%",
                    "Family Group": str(get_family(num)),
                    "Strength": "🔥 HIGH" if rate >= 10 else "⚡ MEDIUM"
                })

            for num, count in top_2d_counts.items():
                rate = round((count / tot_d2_opps) * 100, 2) if tot_d2_opps > 0 else 0
                summary_table.append({
                    "प्रकार": "2-Day Follow-up",
                    "Target Num": f"{last_result:02d}",
                    "Follow-up Number": f"{num:02d}",
                    "कुल आवृत्ति (Frequency)": f"{count} बार",
                    "Observed Rate %": f"{rate}%",
                    "Family Group": str(get_family(num)),
                    "Strength": "🔥 HIGH" if rate >= 10 else "⚡ MEDIUM"
                })
                
            st.table(pd.DataFrame(summary_table))
