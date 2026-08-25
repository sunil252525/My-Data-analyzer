import streamlit as st
import pandas as pd
from collections import Counter

st.set_page_config(page_title="13-Year Target Repeat & Family Detector", layout="wide")

st.title("🎯 13-Year Target Number Repeat & Family Detector")

# ================= HELPER FUNCTIONS =================
RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi_digit(d):
    try: return RASHI_MAP.get(int(d), int(d))
    except: return 0

def get_family(num):
    """राशि + अलट-पलट के साथ 8 जोड़ियों की फैमिली जनरेट करता है"""
    try:
        if pd.isna(num): return []
        num = int(num)
        if not (0 <= num <= 99): return []
        d1, d2 = num // 10, num % 10
        r1, r2 = get_rashi_digit(d1), get_rashi_digit(d2)
        fam = set()
        for a, b in [(d1, d2), (d1, r2), (r1, d2), (r1, r2)]:
            fam.add(a * 10 + b)
            fam.add(b * 10 + a)
        return sorted(list(fam))
    except: return []

def get_family_head(num):
    """किसी भी नंबर की मेन पहचान/फैमिली हेड"""
    fam = get_family(num)
    return fam[0] if fam else num

# ================= TARGET SCANNER ENGINE =================
def analyze_target_occurrences(df, target_game, target_num, window_days=2):
    """
    चुने हुए सटीक गेम में Target Number ढूँढकर विश्लेषण करता है
    """
    next_day_results = []
    window_results = []
    occurrences_log = []

    date_col = 'Date' if 'Date' in df.columns else None
    
    # केवल चुनिंदा गेम की वैध रो (Rows) निकालें
    valid_df = df[[target_game] + ([date_col] if date_col else [])].dropna(subset=[target_game]).reset_index(drop=True)
    total_rows = len(valid_df)

    for idx in range(total_rows):
        val = valid_df.loc[idx, target_game]
        if pd.notna(val) and int(val) == target_num:
            rec_date = valid_df.loc[idx, date_col] if date_col else f"Row #{idx}"
            
            # 1. अगला 1 दिन
            next_1_val = None
            if idx + 1 < total_rows and pd.notna(valid_df.loc[idx + 1, target_game]):
                next_1_val = int(valid_df.loc[idx + 1, target_game])
                next_day_results.append(next_1_val)

            # 2. Window Days के अंदर आए नंबर
            win_vals = []
            for d in range(1, window_days + 1):
                if idx + d < total_rows and pd.notna(valid_df.loc[idx + d, target_game]):
                    v = int(valid_df.loc[idx + d, target_game])
                    win_vals.append(v)
                    window_results.append(v)

            occurrences_log.append({
                "तारीख / रो": rec_date,
                "गेम": target_game,
                "टारगेट नंबर": f"{target_num:02d}",
                "अगला दिन (+1 Day)": f"{next_1_val:02d}" if next_1_val is not None else "N/A",
                "2 दिन के अंदर": ", ".join([f"{v:02d}" for v in win_vals])
            })

    return occurrences_log, next_day_results, window_results


# ================= SIDEBAR & FILE UPLOAD =================
st.sidebar.title("📌 फ़ाइल अपलोड")
uploaded_file = st.sidebar.file_uploader("13 साल की CSV फ़ाइल अपलोड करें", type=["csv"], key="target_page_uploader")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    date_col = 'Date' if 'Date' in df.columns else None
    
    game_order = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in game_order if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    st.subheader("⚙️ पैटर्न सर्च सेटिंग्स:")
    
    col_sel1, col_sel2, col_sel3 = st.columns(3)
    
    with col_sel1:
        selected_game = st.selectbox("🎯 गेम चुनें:", available_cols, index=available_cols.index('GALI') if 'GALI' in available_cols else 0)
    
    with col_sel2:
        target_number = st.number_input("🔢 टारगेट नंबर दर्ज करें (जैसे 25):", min_value=0, max_value=99, value=25, step=1)
        
    with col_sel3:
        window_days = st.slider("📅 कितने दिन के अंदर देखना है (Window):", min_value=1, max_value=5, value=2)

    st.markdown("---")

    # एनालिसिस चलाएं
    logs, next_day_list, window_list = analyze_target_occurrences(df, selected_game, target_number, window_days)

    if logs:
        st.success(f"📊 **13 साल के डेटा में `{selected_game}` में `{target_number:02d}` कुल `{len(logs)}` बार आया है।**")
        
        # --- 1. गणना (Counting Logic) ---
        single_counts = Counter(window_list)
        top_3_tuples = single_counts.most_common(3)
        
        top_3_singles = [item[0] for item in top_3_tuples]
        top_3_singles_str = ", ".join([f"{n:02d}" for n in top_3_singles])

        # Top Families Frequency
        family_counts = Counter([get_family_head(num) for num in window_list])
        top_family_tuples = family_counts.most_common(3)
        top_families_heads = [item[0] for item in top_family_tuples]
        
        # Top फैमिलियों की सभी जोड़ियों का सेट
        all_top_family_pairs = set()
        for f_head in top_families_heads:
            all_top_family_pairs.update(get_family(f_head))
            
        top_family_pairs_sorted = sorted(list(all_top_family_pairs))
        top_family_pairs_str = ", ".join([f"{n:02d}" for n in top_family_pairs_sorted])

        # --- 2. कॉपी-पेस्ट के 2 अलग डब्बे ---
        col_box1, col_box2 = st.columns(2)

        with col_box1:
            st.markdown(f"🔥 **1. `{selected_game}` में `{target_number:02d}` के 2 दिन के अंदर सबसे ज्यादा आए Top 3 नंबर:**")
            st.text_area("कॉपी करें (Top 3 Single Repeat Numbers):", value=top_3_singles_str, height=130, key=f"txt_single_{selected_game}_{target_number}")
            
            st.markdown("**Top 3 नंबरों की फ्रीक्वेंसी:**")
            for num, count in top_3_tuples:
                st.write(f"- नंबर **`{num:02d}`**: कुल **{count}** बार आया")

        with col_box2:
            st.markdown(f"👑 **2. सबसे ज्यादा रिपीट होने वाली Top फैमिलियों की संपूर्ण जोड़ियाँ:**")
            st.text_area("कॉपी करें (Top Repeat Family Numbers):", value=top_family_pairs_str, height=130, key=f"txt_family_{selected_game}_{target_number}")
            
            st.markdown("**Top 3 फैमिलियों की फ्रीक्वेंसी:**")
            for f_head, count in top_family_tuples:
                st.write(f"- **`{f_head:02d}`** की फैमिली: कुल **{count}** बार पास हुई")

        st.markdown("---")
        st.subheader(f"📜 {selected_game} का पूरा रिकॉर्ड (Target Occurrence Records):")
        st.dataframe(pd.DataFrame(logs), use_container_width=True)

    else:
        st.warning(f"⚠️ `{selected_game}` के रिकॉर्ड में नंबर `{target_number:02d}` कभी नहीं मिला।")

else:
    st.info("👈 बाएँ साइडबार से 13 साल की CSV फ़ाइल अपलोड करके शुरू करें।")
    
