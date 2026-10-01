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

                    in_harufs = list(in_h_top2.index)
                    out_harufs = list(out_h_top2.index)

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

                    all_24h_haruf_nums = crossed_24h_direct + haruf_24h_pairs
                    all_24h_haruf_plat = [get_plat(p) for p in all_24h_haruf_nums]

                    crossed_pairs_2x2_direct = [f"{i}{o}" for i in in_harufs for o in out_harufs]
                    crossed_pairs_2x2_plat = [get_plat(p) for p in crossed_pairs_2x2_direct]

                    all_harufs = list(dict.fromkeys(in_harufs + out_harufs))
                    haruf_pairs = [f"{h}{h}" for h in all_harufs]

                    top_1d_direct = [f"{num:02d}" for num in top_1d.index]
                    top_1d_plat = [get_plat(n) for n in top_1d_direct]

                    top_2d_direct = [f"{num:02d}" for num in top_2d.index]
                    top_2d_plat = [get_plat(n) for n in top_2d_direct]

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
                    
                    line_2x2_dir = ", ".join(crossed_pairs_2x2_direct)
                    line_2x2_plt = ", ".join(crossed_pairs_2x2_plat)
                    
                    line_pairs = ", ".join(haruf_pairs)
                    
                    line_d1_dir = ", ".join(top_1d_direct)
                    line_d1_plt = ", ".join(top_1d_plat)
                    
                    line_d2_dir = ", ".join(top_2d_direct)
                    line_d2_plt = ", ".join(top_2d_plat)

                    line_24h_dir = ", ".join(top_24h_direct)
                    line_24h_plt = ", ".join(top_24h_plat)

                    line_24h_haruf_dir = ", ".join(all_24h_haruf_nums)
                    line_24h_haruf_plt = ", ".join(all_24h_haruf_plat)

                    with c_box1:
                        st.markdown("**🎯 हरूफ 2x2 क्रॉसिंग (4 जोड़ी सीधी + पलट):**")
                        st.code(f"{line_2x2_dir}\n{line_2x2_plt}", language="text")

                        st.markdown("**📋 1-Day Follow-up Numbers (सीधी + पलट):**")
                        st.code(f"{line_d1_dir}\n{line_d1_plt}", language="text")

                        st.markdown("**⚡ 24-Hour All-Games Numbers (24 घंटे सभी गेम रिपीट - सीधी + पलट):**")
                        st.code(f"{line_24h_dir}\n{line_24h_plt}", language="text")

                    with c_box2:
                        st.markdown("**👯 हरूफ के जोड़े (Pairs / Jode):**")
                        st.code(line_pairs, language="text")

                        st.markdown("**📋 2-Day Follow-up Numbers (सीधी + पलट):**")
                        st.code(f"{line_d2_dir}\n{line_d2_plt}", language="text")

                        st.markdown("**🎲 24-Hour Haruf Numbers & Pairs (24 घंटे हर्फ़ के नंबर और जोड़े - सीधी + पलट):**")
                        st.code(f"{line_24h_haruf_dir}\n{line_24h_haruf_plt}", language="text")

                    st.markdown("---")

                    # ----------------------------------------------------
                    # 3. ALL-IN-ONE COMBINED BOX WITH DYNAMIC COUNT STATS
                    # ----------------------------------------------------
                    st.markdown("### 🔥 ऑल-इन-वन कंबाइंड नंबर बॉक्स (All-in-One Structured Box)")

                    raw_lines = [
                        crossed_pairs_2x2_direct,
                        crossed_pairs_2x2_plat,
                        haruf_pairs,
                        top_1d_direct,
                        top_1d_plat,
                        top_2d_direct,
                        top_2d_plat,
                        top_24h_direct,
                        top_24h_plat,
                        all_24h_haruf_nums,
                        all_24h_haruf_plat
                    ]

                    all_comb_numbers = [item.strip() for sublist in raw_lines for item in sublist if item.strip()]
                    
                    total_box_count = len(all_comb_numbers)
                    unique_box_count = len(set(all_comb_numbers))
                    same_to_same_matches = total_box_count - unique_box_count

                    st.success(
                        f"📊 **ऑल-इन-वन बॉक्स समरी:**\n"
                        f"• **कुल दर्ज नंबर (Total Numbers):** {total_box_count}\n"
                        f"• **सेम टू सेम (Duplicate):** {same_to_same_matches} नंबर\n"
                        f"• **यूनिक नंबर (Unique Numbers):** {unique_box_count}"
                    )

                    all_in_one_text = "\n".join([", ".join(l) for l in raw_lines if l])

                    st.code(all_in_one_text, language="text")

                    # ----------------------------------------------------
                    # 4. PATTERN-PRESERVING UNIQUE COMBINED BOX WITH WHATSAPP LINK
                    # ----------------------------------------------------
                    st.markdown("### 🎯 ऑल-इन-वन पैटर्न यूनिक बॉक्स (Pattern Preserved - Duplicate Removed)")

                    seen_numbers = set()
                    unique_pattern_lines = []

                    for line in raw_lines:
                        filtered_line = []
                        for num in line:
                            num_clean = num.strip()
                            # 100% सटीक जांच: यदि यह नंबर पहली बार आया है तो ही जोड़ें
                            if num_clean and num_clean not in seen_numbers:
                                filtered_line.append(num_clean)
                                seen_numbers.add(num_clean)
                        
                        if filtered_line:
                            unique_pattern_lines.append(", ".join(filtered_line))

                    final_unique_count = len(seen_numbers)

                    st.info(
                        f"🔢 **यूनिक पैटर्न बॉक्स गिनती (Total Unique Numbers Count):**\n"
                        f"• **कुल यूनिक नंबर (Total Numbers):** **{final_unique_count}**"
                    )

                    unique_pattern_box_text = "\n".join(unique_pattern_lines)

                    st.code(unique_pattern_box_text, language="text")

                    # --- WHATSAPP SHARE LINK GENERATOR ---
                    msg_text = f"🎯 *{col} - Unique Pattern Numbers* (Total: {final_unique_count})\n\n{unique_pattern_box_text}"
                    encoded_msg = urllib.parse.quote(msg_text)
                    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_msg}"

                    # Clickable WhatsApp Link Button
                    st.markdown(
                        f'<a href="{whatsapp_url}" target="_blank">'
                        f'<button style="background-color:#25D366; color:white; border:none; padding:12px 24px; '
                        f'font-size:16px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%;">'
                        f'📲 WhatsApp पर भेजें (Click to Share on WhatsApp)'
                        f'</button></a>',
                        unsafe_allow_html=True
                    )

                    st.markdown("---")

                    # ----------------------------------------------------
                    # 5. STRUCTURED TABLE OUTPUT
                    # ----------------------------------------------------
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
                        st.info(f"Observed Rate >= {min_rate_filter}% का कोई रिकॉर्ड नहीं मिला।")
                    
