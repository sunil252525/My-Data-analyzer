import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse

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

# Helper function to get Inside/Outside Haruf
def get_haruf(num):
    try:
        num = int(num)
        return num // 10, num % 10
    except:
        return None, None

# Helper function to safely reverse (Palat) a number string formatted to 2 digits
def get_plat(num_val):
    try:
        num_str = f"{int(num_val):02d}"
        return num_str[::-1]
    except:
        return ""

# Helper to format a line with rate at the end
def fmt_line(num_list, rate):
    clean_nums = []
    for n in num_list:
        try:
            clean_nums.append(f"{int(n):02d}")
        except:
            clean_nums.append(str(n))
    if not clean_nums:
        return ""
    return f"{', '.join(clean_nums)} ({rate})"

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    st.success("✅ डेटाबेस सफलतापूर्वक लोड हो गया!")

    # ----------------------------------------------------
    # 2. Scan Parameters
    # ----------------------------------------------------
    st.markdown("---")
    st.subheader("⚙️ स्कैन पैरामीटर्स (Scan Parameters)")
    
    col1, col2 = st.columns([2, 2])
    
    with col1:
        min_rate_filter = st.slider("न्यूनतम Observed Rate % फ़िल्टर", 10, 100, 100)
        
    with col2:
        st.info("💡 सिस्टम हर गेम का सबसे आख़िरी रिजल्ट स्वतः (Automatically) फ़ेच करेगा।")

    run_scan = st.button("🔥 Run Multi-Game Auto Scan (एक साथ सभी गेम देखें)", use_container_width=True)

    if run_scan:
        st.markdown("---")
        
        tabs = st.tabs([f"🎯 {col}" for col in available_cols])
        
        # 24 घंटे के सभी गेम्स के डेटा को एकत्र करने के लिए लिस्ट
        all_games_24h_summary = []
        
        for idx, col in enumerate(available_cols):
            with tabs[idx]:
                valid_series = df[col].dropna().astype(int)
                
                if valid_series.empty:
                    st.warning(f"{col} में कोई वैध डेटा नहीं है।")
                    continue
                
                last_result = valid_series.iloc[-1]
                t_idx = df[df[col] == last_result].index
                total_hist_count = len(t_idx)
                
                # ----------------------------------------------------
                # A. 1-DAY AND 2-DAY SINGLE-GAME SCAN LOGIC
                # ----------------------------------------------------
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
                    
                    in_h_top2 = d1_vals.apply(lambda x: x // 10).value_counts().head(2)
                    out_h_top2 = d1_vals.apply(lambda x: x % 10).value_counts().head(2)

                    in_harufs = list(in_h_top2.index)[:2]
                    out_harufs = list(out_h_top2.index)[:2]

                    # ----------------------------------------------------
                    # EXACT 16-NUMBER CROSSING ENGINE (3 LINES)
                    # ----------------------------------------------------
                    crossed_line1 = [f"{i}{o}" for i in in_harufs for o in out_harufs]
                    crossed_line2 = [f"{o}{i}" for i in in_harufs for o in out_harufs]

                    all_cross_digits = list(dict.fromkeys(in_harufs + out_harufs))
                    total_16_cross = [f"{d1}{d2}" for d1 in all_cross_digits for d2 in all_cross_digits]

                    seen_cross = set()
                    l1_clean, l2_clean = [], []

                    for num in crossed_line1:
                        if num not in seen_cross:
                            l1_clean.append(num)
                            seen_cross.add(num)

                    for num in crossed_line2:
                        if num not in seen_cross:
                            l2_clean.append(num)
                            seen_cross.add(num)

                    l3_clean = [num for num in total_16_cross if num not in seen_cross]
                    pairs_list = [f"{h}{h}" for h in all_cross_digits]

                    # ----------------------------------------------------
                    # B. 24-HOUR ALL-GAMES ENGINE LOGIC
                    # ----------------------------------------------------
                    next_24h_numbers, haruf_in_24h, haruf_out_24h = [], [], []

                    for match_i in t_idx:
                        if match_i + 1 < len(df):
                            for c_24 in available_cols:
                                val_24 = df.loc[match_i + 1, c_24]
                                if pd.notna(val_24):
                                    val_int = int(val_24)
                                    next_24h_numbers.append(val_int)
                                    h_i, h_o = get_haruf(val_int)
                                    if h_i is not None: haruf_in_24h.append(h_i)
                                    if h_o is not None: haruf_out_24h.append(h_o)

                    top_24h_series = pd.Series(next_24h_numbers).value_counts().head(5) if next_24h_numbers else pd.Series()
                    top_24h_direct = [f"{num:02d}" for num in top_24h_series.index]
                    top_24h_plat = [get_plat(n) for n in top_24h_direct]

                    top_in_24h = pd.Series(haruf_in_24h).value_counts().head(3).index.tolist() if haruf_in_24h else []
                    top_out_24h = pd.Series(haruf_out_24h).value_counts().head(3).index.tolist() if haruf_out_24h else []

                    crossed_24h_direct = [f"{i}{o}" for i in top_in_24h for o in top_out_24h]
                    all_24h_harufs = list(dict.fromkeys(top_in_24h + top_out_24h))
                    haruf_24h_pairs = [f"{h}{h}" for h in all_24h_harufs]

                    # --- HARUF DEDUPLICATION (कोई रिपीट नंबर/जोड़ा नहीं होगा) ---
                    seen_haruf_nums = set()
                    
                    h_nums_clean = []
                    for n in crossed_24h_direct:
                        if n not in seen_haruf_nums:
                            h_nums_clean.append(n)
                            seen_haruf_nums.add(n)

                    h_plat_clean = []
                    for n in [get_plat(p) for p in crossed_24h_direct]:
                        if n not in seen_haruf_nums:
                            h_plat_clean.append(n)
                            seen_haruf_nums.add(n)

                    for p in haruf_24h_pairs:
                        if p not in seen_haruf_nums:
                            h_plat_clean.append(p)
                            seen_haruf_nums.add(p)

                    top_1d_direct = [f"{num:02d}" for num in top_1d.index]
                    top_1d_plat = [get_plat(n) for n in top_1d_direct]

                    top_2d_direct = [f"{num:02d}" for num in top_2d.index]
                    top_2d_plat = [get_plat(n) for n in top_2d_direct]

                    raw_sections = [
                        (l1_clean, 100),
                        (l2_clean, 50),
                        (l3_clean, 50),
                        (top_1d_direct, 50),
                        (top_1d_plat, 50),
                        (top_2d_direct, 50),
                        (top_2d_plat, 50),
                        (top_24h_direct, 100),
                        (top_24h_plat, 50),
                        (h_nums_clean, 50),
                        (h_plat_clean, 50)
                    ]

                    # ----------------------------------------------------
                    # 1. EXECUTIVE SUMMARY & HISTORICAL STATS
                    # ----------------------------------------------------
                    st.subheader(f"📌 {col} का ऐतिहासिक विश्लेषण (Last Result: {last_result:02d})")
                    st.write(f"• **मुख्य ऐतिहासिक निष्कर्ष:** 13 साल के रिकॉर्ड में **{col}** में **{last_result:02d}** कुल **{total_hist_count} बार** आया है।")
                    
                    top_1d_str = ", ".join([f"{k:02d}: {v} बार" for k, v in top_1d.to_dict().items()])
                    top_2d_str = ", ".join([f"{k:02d}: {v} बार" for k, v in top_2d.to_dict().items()])
                    top_24h_str = ", ".join([f"{k:02d}: {v} बार" for k, v in top_24h_series.to_dict().items()])
                    
                    st.write(f"• **सबसे मजबूत 1-Day Follow-up (फ्रीक्वेंसी):** {top_1d_str}")
                    st.write(f"• **सबसे मजबूत 2-Day Follow-up (फ्रीक्वेंसी):** {top_2d_str}")
                    st.write(f"• **24-Hour All-Games Repeat (फ्रीक्वेंसी):** {top_24h_str}")
                    st.write(f"• **24-Hour टॉप अंदर हर्फ़:** {top_in_24h} | **24-Hour टॉप बाहर हर्फ़:** {top_out_24h}")
                    st.write(f"• **फैमिली पासिंग दर:** Observed Rate = **{fam_obs_rate}%**")
                    
                    st.markdown("---")
                    
                    # ----------------------------------------------------
                    # 2. INDIVIDUAL CATEGORY BOXES
                    # ----------------------------------------------------
                    st.markdown("### 📋 अलग-अलग कैटेगरी बॉक्स")
                    
                    c_box1, c_box2 = st.columns(2)

                    with c_box1:
                        st.markdown("**🎯 हरूफ़ क्रॉसिंग 16 नंबर (Line 1: 100, Line 2 & 3: 50):**")
                        st.code(
                            f"{fmt_line(l1_clean, 100)}\n"
                            f"{fmt_line(l2_clean, 50)}\n"
                            f"{fmt_line(l3_clean, 50)}", 
                            language="text"
                        )

                        st.markdown("**📋 1-Day Follow-up Numbers (सीधी + पलट):**")
                        st.code(
                            f"{fmt_line(top_1d_direct, 50)}\n"
                            f"{fmt_line(top_1d_plat, 50)}", 
                            language="text"
                        )

                        st.markdown("**⚡ 24-Hour All-Games Numbers (24 घंटे सभी गेम रिपीट - सीधी + पलट):**")
                        st.code(
                            f"{fmt_line(top_24h_direct, 100)}\n"
                            f"{fmt_line(top_24h_plat, 50)}", 
                            language="text"
                        )

                    with c_box2:
                        st.markdown("**👯 हरूफ के जोड़े (Pairs / Jode):**")
                        st.code(fmt_line(pairs_list, 50), language="text")

                        st.markdown("**📋 2-Day Follow-up Numbers (सीधी + पलट):**")
                        st.code(
                            f"{fmt_line(top_2d_direct, 50)}\n"
                            f"{fmt_line(top_2d_plat, 50)}", 
                            language="text"
                        )

                        st.markdown("**🎲 24-Hour Haruf Numbers & Pairs (24 घंटे हर्फ़ के नंबर और जोड़े - सीधी + पलट):**")
                        st.code(
                            f"{fmt_line(h_nums_clean, 50)}\n"
                            f"{fmt_line(h_plat_clean, 50)}", 
                            language="text"
                        )

                    st.markdown("---")

                    # ----------------------------------------------------
                    # 3. ALL-IN-ONE COMBINED BOX WITH DYNAMIC COUNT STATS
                    # ----------------------------------------------------
                    st.markdown("### 🔥 ऑल-इन-वन कंबाइंड नंबर बॉक्स (All-in-One Structured Box)")

                    all_combined_lines_str = []
                    total_box_count = 0
                    seen_base_nums = set()

                    for n_list, rate in raw_sections:
                        if n_list:
                            all_combined_lines_str.append(fmt_line(n_list, rate))
                            total_box_count += len(n_list)
                            for item in n_list:
                                seen_base_nums.add(item)

                    unique_count = len(seen_base_nums)
                    same_to_same_matches = total_box_count - unique_count

                    st.success(
                        f"📊 **ऑल-इन-वन बॉक्स समरी:**\n"
                        f"• **कुल दर्ज नंबर (Total Numbers):** {total_box_count}\n"
                        f"• **सेम टू सेम (Duplicate):** {same_to_same_matches} नंबर\n"
                        f"• **यूनिक नंबर (Unique Numbers):** {unique_count}"
                    )

                    all_in_one_text = "\n".join(all_combined_lines_str)
                    st.code(all_in_one_text, language="text")

                    # ----------------------------------------------------
                    # 4. PATTERN-PRESERVING UNIQUE COMBINED BOX
                    # ----------------------------------------------------
                    st.markdown("### 🎯 ऑल-इन-वन पैटर्न यूनिक बॉक्स (Pattern Preserved - Duplicate Removed)")

                    seen_base = set()
                    unique_pattern_lines = []
                    count_100 = 0
                    count_50 = 0

                    for n_list, rate in raw_sections:
                        filtered_nums = []
                        for num in n_list:
                            if num not in seen_base:
                                seen_base.add(num)
                                filtered_nums.append(num)
                                if rate == 100:
                                    count_100 += 1
                                elif rate == 50:
                                    count_50 += 1
                        
                        if filtered_nums:
                            unique_pattern_lines.append(fmt_line(filtered_nums, rate))

                    final_unique_count = len(seen_base)

                    # --- PAYMENT CALCULATION ENGINE ---
                    total_100_amt = count_100 * 100
                    total_50_amt = count_50 * 50
                    grand_total_payment = total_100_amt + total_50_amt

                    st.info(
                        f"🔢 **यूनिक पैटर्न बॉक्स गिनती एवं पेमेंट समरी (Payment Summary):**\n"
                        f"• **कुल यूनिक नंबर:** **{final_unique_count}**\n"
                        f"• **(100) वाले नंबर:** {count_100} × 100 = **₹{total_100_amt}**\n"
                        f"• **(50) वाले नंबर:** {count_50} × 50 = **₹{total_50_amt}**\n"
                        f"• 💰 **कुल पेमेंट (Grand Total):** **₹{grand_total_payment}**"
                    )

                    unique_pattern_box_text = "\n".join(unique_pattern_lines)
                    st.code(unique_pattern_box_text, language="text")

                    # --- EXACT WHATSAPP FORMAT AS REQUESTED BY USER ---
                    game_24h_str = (
                        f"🎮 *{col}*⚡\n"
                        f"{fmt_line(top_24h_direct, 100)}\n"
                        f"{fmt_line(top_24h_plat, 50)}\n\n"
                        f"🎲\n"
                        f"{fmt_line(h_nums_clean, 50)}\n"
                        f"{fmt_line(h_plat_clean, 50)}"
                    )
                    all_games_24h_summary.append(game_24h_str)

        # ----------------------------------------------------
        # ALL GAMES SUMMARY & SINGLE WHATSAPP SHARE BUTTON
        # ----------------------------------------------------
        st.markdown("---")
        st.subheader("📲 सभी गेम्स का 24-घंटे वाला बॉक्स एक साथ भेजें (All-Game WhatsApp Sender)")
        
        full_whatsapp_msg = "\n\n".join(all_games_24h_summary)
        
        encoded_all_msg = urllib.parse.quote(full_whatsapp_msg)
        all_whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_all_msg}"

        st.markdown(
            f'<a href="{all_whatsapp_url}" target="_blank">'
            f'<button style="background-color:#25D366; color:white; border:none; padding:15px 30px; '
            f'font-size:18px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%;">'
            f'📲 सभी गेम्स (ALL GAMES 24H BOXES) को एक साथ WhatsApp पर शेयर करें'
            f'</button></a>',
            unsafe_allow_html=True
                )
                    
