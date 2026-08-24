import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Monthly Single-Day & Family Formula", layout="wide")

st.title("📅 मंथली कस्टम पैटर्न फ़ॉर्मूला (1-Day Same-to-Same & Family)")

# Custom CSS for Horizontal Scrolling Cards
st.markdown("""
<style>
    .scroll-container {
        display: flex;
        overflow-x: auto;
        gap: 15px;
        padding: 10px 0px;
    }
    .scroll-card {
        min-width: 280px;
        max-width: 320px;
        background-color: #1e222d;
        border: 1px solid #363b4e;
        border-radius: 10px;
        padding: 12px;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# ================= HELPER FUNCTIONS =================
RASHI_MAP = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 0, 6: 1, 7: 2, 8: 3, 9: 4}

def get_rashi_digit(d):
    try: return RASHI_MAP.get(int(d), int(d))
    except: return 0

def get_family(num):
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

# ================= SIDEBAR & FILE UPLOAD =================
st.sidebar.title("📌 फ़ाइल अपलोड")
uploaded_file = st.sidebar.file_uploader("CSV फ़ाइल अपलोड करें", type=["csv"], key="monthly_uploader")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    date_col = 'Date' if 'Date' in df.columns else None
    
    game_order = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in game_order if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=available_cols, how='all').reset_index(drop=True)

    if "selected_game_m" not in st.session_state or st.session_state["selected_game_m"] not in available_cols:
        st.session_state["selected_game_m"] = available_cols[0]

    st.subheader("🎯 गेम चुनें (Delhi Bazaar / SG / FB आदि):")
    cols = st.columns(len(available_cols))
    for idx, col_name in enumerate(available_cols):
        recent_val = df[col_name].dropna().iloc[-1] if not df[col_name].dropna().empty else 0
        with cols[idx]:
            is_active = (st.session_state["selected_game_m"] == col_name)
            btn_label = f"✅ {col_name} ({int(recent_val):02d})" if is_active else f"📌 {col_name} ({int(recent_val):02d})"
            if st.button(btn_label, key=f"btn_m_{col_name}", use_container_width=True):
                st.session_state["selected_game_m"] = col_name

    active_g = st.session_state["selected_game_m"]
    st.markdown("---")

    # ---------------- 2 MAIN SECTIONS TABS ----------------
    tab1, tab2 = st.tabs([
        "1️⃣ सेम-टू-सेम (1-दिन) पूरे महीने के ऑल-डेट्स रिजल्ट्स", 
        "2️⃣ फैमिली पैटर्न (कस्टम दिन + साइड-बाई-साइड स्क्रॉल)"
    ])

    # ================= FEATURE 1: 1-DAY SAME TO SAME =================
    with tab1:
        st.subheader(f"📊 `{active_g}` - 1-Day Same-to-Same Daily Results")
        st.caption("महीने की 1 तारीख से लेकर आख़िरी तारीख तक के हर दिन का 1-दिन पैटर्न रिजल्ट:")

        series_vals = df[active_g].tolist()
        total_rows = len(df)
        
        # हॉरिजॉन्टल स्क्रॉल कार्ड्स कंटेनर
        scroll_html = '<div class="scroll-container">'
        
        for idx in range(1, total_rows):
            curr_date = df.loc[idx, date_col] if date_col else f"Row #{idx}"
            prev_val = series_vals[idx - 1]
            
            if pd.isna(prev_val): continue
            prev_val = int(prev_val)
            
            # पूरे डेटाबेस में इस नंबर (1-Day Same-to-Same) के बाद क्या-क्या आया
            matched_next_results = []
            for i in range(idx - 1):
                if pd.notna(series_vals[i]) and int(series_vals[i]) == prev_val:
                    if pd.notna(series_vals[i + 1]):
                        matched_next_results.append(int(series_vals[i + 1]))
                        
            clean_nums = sorted(list(set(matched_next_results)))
            nums_str = ", ".join([f"{n:02d}" for n in clean_nums]) if clean_nums else "कोई मैच नहीं"

            scroll_html += f"""
            <div class="scroll-card">
                <h4>📅 {curr_date}</h4>
                <p><b>पिछला नंबर:</b> <span style="color:#00ffcc;">{prev_val:02d}</span></p>
                <p><b>कॉपी वाले कुल नंबर ({len(clean_nums)}):</b></p>
                <div style="background:#12141c; padding:8px; border-radius:5px; font-family:monospace; font-size:12px; word-break:break-all; max-height:100px; overflow-y:auto;">
                    {nums_str}
                </div>
            </div>
            """
        scroll_html += '</div>'
        st.markdown(scroll_html, unsafe_allow_html=True)

    # ================= FEATURE 2: FAMILY PATTERN WITH HORIZONTAL SCROLL =================
    with tab2:
        st.subheader(f"👨‍👩‍👧‍👦 `{active_g}` - फैमिली पैटर्न (कस्टम दिन + साइड स्क्रॉल)")
        fam_days = st.slider("🎛️ फैमिली लड़ी के दिन चुनें:", min_value=1, max_value=10, value=3, key="monthly_fam_slider")

        series_vals = df[active_g].tolist()
        total_rows = len(df)
        
        scroll_html_fam = '<div class="scroll-container">'
        
        for idx in range(fam_days, total_rows):
            curr_date = df.loc[idx, date_col] if date_col else f"Row #{idx}"
            target_seq = series_vals[idx - fam_days : idx]
            
            if any(pd.isna(v) for v in target_seq): continue
            target_seq = [int(v) for v in target_seq]
            
            # फैमिली मैचिंग लॉजिक
            target_fam_sets = [set(get_family(v)) for v in target_seq]
            
            matched_next_results = []
            for i in range(total_rows - fam_days - 1):
                sub_seq = series_vals[i : i + fam_days]
                if any(pd.isna(v) for v in sub_seq): continue
                sub_seq = [int(v) for v in sub_seq]
                
                # फैमिली चेक
                is_match = True
                for d in range(fam_days):
                    if not (set(get_family(sub_seq[d])) & target_fam_sets[d]):
                        is_match = False
                        break
                
                if is_match and pd.notna(series_vals[i + fam_days]):
                    matched_next_results.append(int(series_vals[i + fam_days]))
            
            clean_nums = sorted(list(set(matched_next_results)))
            
            # फैमिली ब्लॉक लिस्ट (सभी नंबरों की 8-8 जोड़ियाँ)
            all_family_blocked = set()
            for n in clean_nums:
                all_family_blocked.update(get_family(n))
                
            nums_str = ", ".join([f"{n:02d}" for n in clean_nums]) if clean_nums else "कोई मैच नहीं"
            fam_str = ", ".join([f"{n:02d}" for n in sorted(list(all_family_blocked))]) if all_family_blocked else "N/A"

            scroll_html_fam += f"""
            <div class="scroll-card">
                <h4>📅 {curr_date}</h4>
                <p><b>लड़ी ({fam_days} दिन):</b> <span style="color:#ffcc00;">{target_seq}</span></p>
                <p><b>Next Results ({len(clean_nums)}):</b></p>
                <div style="background:#12141c; padding:6px; border-radius:5px; font-family:monospace; font-size:11px; word-break:break-all; max-height:70px; overflow-y:auto; margin-bottom:8px;">
                    {nums_str}
                </div>
                <p><b>कुल फैमिली जोड़ियाँ ({len(all_family_blocked)}):</b></p>
                <div style="background:#2a1a1a; color:#ff8888; padding:6px; border-radius:5px; font-family:monospace; font-size:11px; word-break:break-all; max-height:70px; overflow-y:auto;">
                    {fam_str}
                </div>
            </div>
            """
        scroll_html_fam += '</div>'
        st.markdown(scroll_html_fam, unsafe_allow_html=True)

else:
    st.info("👈 बाएँ साइडबार से CSV फ़ाइल अपलोड करें।")
