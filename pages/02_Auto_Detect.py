import streamlit as st
import pandas as pd
import numpy as np
import urllib.parse

st.set_page_config(page_title="Auto-Detect Sequence Dashboard", layout="wide")

st.title("⚡ ऑटो-डिटेक्ट एडवांस डैशबोर्ड (Fully Automatic)")

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

def get_haruf(num):
    try:
        if pd.isna(num): return None, None
        num = int(num)
        if not (0 <= num <= 99): return None, None
        return num // 10, num % 10
    except: return None, None

def get_haruf_and_rashi_set(num):
    try:
        if pd.isna(num): return set()
        num = int(num)
        if not (0 <= num <= 99): return set()
        d1, d2 = num // 10, num % 10
        r1, r2 = get_rashi_digit(d1), get_rashi_digit(d2)
        return {d1, d2, r1, r2}
    except: return set()

def check_single_match(mode_id, hist_val, rec_pattern):
    try:
        hist_val = int(hist_val)
        if mode_id == "1": return bool(rec_pattern & get_haruf_and_rashi_set(hist_val))
        elif mode_id == "2":
            h_i, h_o = get_haruf(hist_val)
            hist_set = {h_i, h_o} if h_i is not None else set()
            return bool(rec_pattern & hist_set)
        elif mode_id == "3": return hist_val == rec_pattern
        elif mode_id == "4": return hist_val in rec_pattern
        elif mode_id == "5": return bool(rec_pattern & set(get_family(hist_val)))
    except: return False
    return False

# ================= FAST CACHED SEARCH ENGINE =================
@st.cache_data
def run_fast_sequence_search(df, g_sel, available_cols, date_col, mode_id, mode_seq_days):
    clean_series = df[g_sel].dropna().astype(int).tolist()
    max_possible_days = len(clean_series)
    recent_nums = clean_series[-mode_seq_days:] if max_possible_days >= mode_seq_days else clean_series

    recent_patterns = []
    for n in recent_nums:
        if mode_id == "1": recent_patterns.append(get_haruf_and_rashi_set(n))
        elif mode_id == "2":
            h_i, h_o = get_haruf(n)
            recent_patterns.append({h_i, h_o} if h_i is not None else set())
        elif mode_id == "3": recent_patterns.append(int(n))
        elif mode_id == "4":
            rev_n = int(f"{int(n):02d}"[::-1])
            recent_patterns.append({int(n), rev_n})
        elif mode_id == "5": recent_patterns.append(set(get_family(n)))

    matched_records = []
    seen_rows = set()

    for col in available_cols:
        col_vals = df[col].tolist()
        n_vals = len(col_vals)
        end_idx_limit = n_vals - len(recent_nums) - 1

        for i in range(end_idx_limit):
            target_idx = i + len(recent_nums)
            if (col, target_idx) in seen_rows: continue

            sub_seq = col_vals[i : target_idx]
            if any(pd.isna(v) for v in sub_seq): continue
            sub_seq = [int(v) for v in sub_seq]
            
            is_match = True
            for day_idx in range(len(recent_nums)):
                if not check_single_match(mode_id, sub_seq[day_idx], recent_patterns[day_idx]):
                    is_match = False
                    break

            if is_match:
                next_val = col_vals[target_idx]
                if pd.notna(next_val):
                    rec_date = df.loc[target_idx, date_col] if date_col else f"Row #{target_idx}"
                    matched_records.append({
                        "तारीख / रो": rec_date,
                        "गेम का नाम": col,
                        "सटीक लड़ी": str(sub_seq),
                        "Next Result": int(next_val)
                    })
                    seen_rows.add((col, target_idx))

    return matched_records, recent_nums

# ================= AUTO-DETECT OPTIMAL SEQUENCE LENGTH =================
def find_auto_best_sequence(df, g_sel, available_cols, date_col, mode_id, max_check_days=15):
    """
    यह फ़ंक्शन खुद बैकग्राउंड में चेक करेगा कि सबसे लंबी मैचिंग लड़ी कितने दिनों पर बन रही है (जैसे 12, 10, 8 दिन)।
    """
    for test_days in range(max_check_days, 1, -1):
        matched_records, recent_nums = run_fast_sequence_search(df, g_sel, available_cols, date_col, mode_id, test_days)
        if matched_records:
            return test_days, matched_records, recent_nums
    
    # अगर लंबी लड़ी नहीं मिली तो डिफ़ॉल्ट 2 दिन पर सेट करेगा
    matched_records, recent_nums = run_fast_sequence_search(df, g_sel, available_cols, date_col, mode_id, 2)
    return 2, matched_records, recent_nums

# ================= STATISTICAL ANALYSIS =================
def get_statistically_analyzed_crossing(df, col):
    vals = df[col].dropna().astype(int).tolist()
    if len(vals) < 20:
        return [0, 1, 2, 3, 4, 5], "अपर्याप्त डेटा"

    last_num = vals[-1]
    
    method_scores = {"Method_A": {d: 0 for d in range(10)}, 
                     "Method_B": {d: 0 for d in range(10)}, 
                     "Method_C": {d: 0 for d in range(10)}}

    for i in range(len(vals) - 2):
        if vals[i] == last_num:
            f1, f2 = vals[i+1], vals[i+2]
            for h in [f1//10, f1%10, f2//10, f2%10]:
                if 0 <= h <= 9: method_scores["Method_A"][h] += 1

    for idx, num in enumerate(vals[-15:]):
        h1, h2 = num // 10, num % 10
        weight = idx + 1
        method_scores["Method_B"][h1] += weight
        method_scores["Method_B"][h2] += weight

    for num in vals[-10:]:
        d1, d2 = num // 10, num % 10
        r1, r2 = get_rashi_digit(d1), get_rashi_digit(d2)
        for h in [d1, d2, r1, r2]:
            method_scores["Method_C"][h] += 1

    accuracy = {"Method_A": 0, "Method_B": 0, "Method_C": 0}
    test_range = range(max(10, len(vals) - 20), len(vals) - 1)

    for t_idx in test_range:
        actual_next = vals[t_idx + 1]
        act_h1, act_h2 = actual_next // 10, actual_next % 10

        for m_name, scores in method_scores.items():
            top_6_m = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:6]
            if act_h1 in top_6_m and act_h2 in top_6_m:
                accuracy[m_name] += 1

    best_method = max(accuracy, key=accuracy.get)
    combined_scores = {d: method_scores["Method_A"][d]*2 + method_scores["Method_B"][d] + method_scores["Method_C"][d]*1.5 for d in range(10)}
    top_6 = sorted(combined_scores.keys(), key=lambda x: combined_scores[x], reverse=True)[:6]
    top_6.sort()
    
    win_percentage = int((accuracy[best_method] / len(test_range)) * 100) if test_range else 0
    analysis_note = f"बेस्ट फ़ॉर्मूला पासिंग दर: {win_percentage}% ({len(test_range)} टेस्ट में)"

    return top_6, analysis_note

# ================= SIDEBAR & FILE UPLOAD =================
st.sidebar.title("📌 फ़ाइल अपलोड")
uploaded_file = st.sidebar.file_uploader("CSV फ़ाइल अपलोड करें", type=["csv"], key="dashboard_uploader")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    date_col = 'Date' if 'Date' in df.columns else None
    
    game_order = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in game_order if c in df.columns]
    
    for c in available_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=available_cols, how='all').reset_index(drop=True)

    if "selected_game" not in st.session_state or st.session_state["selected_game"] not in available_cols:
        st.session_state["selected_game"] = available_cols[0]

    st.subheader("📦 गेम-वाइज़ रिकॉर्ड बॉक्सेज़ (क्लिक करें):")
    
    cols = st.columns(len(available_cols))
    for idx, col_name in enumerate(available_cols):
        recent_5 = df[col_name].dropna().tail(5).astype(int).tolist()
        recent_str = " - ".join([f"{n:02d}" for n in recent_5])
        
        with cols[idx]:
            is_active = (st.session_state["selected_game"] == col_name)
            box_label = f"📌 {col_name}\n\n{recent_str}" if not is_active else f"✅ {col_name}\n\n{recent_str}"
            if st.button(box_label, key=f"btn_{col_name}", use_container_width=True):
                st.session_state["selected_game"] = col_name

    active_g = st.session_state["selected_game"]
    st.markdown("---")

    # ---------------- MAIN SECTION TABS ----------------
    main_tab1, main_tab2, main_tab3 = st.tabs(["📊 ऑटो-डिटेक्टेड लड़ी पैटर्न", "🤖 ऑटो 6-हरूफ़ स्मार्ट क्रॉसिंग", "⚡ ऑटो-डिटेक्ट Rare Number 24H"])

    # ================= TAB 1: MANUAL SEQUENCE PATTERNS =================
    with main_tab1:
        st.markdown("💡 **नोट:** अब आपको स्लाइडर खिसकाने की ज़रूरत नहीं है! सिस्टम खुद ताज़ा और सबसे सटीक लड़ी पर ऑटो-सेट हो जाता है।")
        
        use_manual = st.checkbox("⚙️ अगर खुद स्लाइडर से दिन सेट करना चाहें तो यहाँ टिक करें")
        manual_days = 5
        if use_manual:
            manual_days = st.slider("🎛️ दिन चुनें:", min_value=1, max_value=20, value=5, key="global_seq_slider")

        sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5 = st.tabs([
            "1️⃣ हर्फ़ + राशि", "2️⃣ केवल हर्फ़", "3️⃣ सेम टू सेम", "4️⃣ अलट-पलट", "5️⃣ फैमिली"
        ])

        modes = [
            ("1", sub_tab1, "hr"), ("2", sub_tab2, "h"), 
            ("3", sub_tab3, "exact"), ("4", sub_tab4, "flip"), ("5", sub_tab5, "fam")
        ]

        for mode_id, t_obj, k_prefix in modes:
            with t_obj:
                if use_manual:
                    auto_days = manual_days
                    matched_records, recent_nums = run_fast_sequence_search(df, active_g, available_cols, date_col, mode_id, auto_days)
                else:
                    auto_days, matched_records, recent_nums = find_auto_best_sequence(df, active_g, available_cols, date_col, mode_id)

                st.info(f"🎯 **{active_g}** ऑटो-सेट लड़ी लंबाई: **`{auto_days} दिन`** | ताज़ा पैटर्न: `{recent_nums}`")

                if matched_records:
                    match_df = pd.DataFrame(matched_records)
                    next_results = match_df["Next Result"].tolist()
                    clean_nums = sorted(list(set(next_results)))
                    box_str = ", ".join([f"{n:02d}" for n in clean_nums])
                    
                    st.success(f"✅ ऑटो-मैच पाए गए: `{len(matched_records)}` बार")

                    # ------------ 🎯 केवल हर्फ़ टैब: ऑटो-क्रॉसिंग जेनरेशन ------------
                    if mode_id == "2":
                        haruf_counts = {d: 0 for d in range(10)}
                        for num_val in next_results:
                            h_in, h_out = get_haruf(num_val)
                            if h_in is not None and 0 <= h_in <= 9: haruf_counts[h_in] += 1
                            if h_out is not None and 0 <= h_out <= 9: haruf_counts[h_out] += 1

                        sorted_harufs = sorted(haruf_counts.keys(), key=lambda d: haruf_counts[d], reverse=True)
                        top_6_harufs = sorted_harufs[:6]
                        top_4_harufs = sorted_harufs[:4]

                        st.markdown("### 👑 ऑटो-सेट लड़ी की मुख्य क्रॉसिंग:")
                        
                        h_rank_str = " > ".join([f"**{h}** ({haruf_counts[h]} बार)" for h in top_6_harufs])
                        st.success(f"📊 **हर्फ़ रैंकिंग:** {h_rank_str}")

                        hc1, hc2 = st.columns(2)
                        with hc1:
                            st.markdown("⚡ **4-हरूफ़ क्रॉसिंग (Top 4):**")
                            st.code(f"[ {', '.join(map(str, sorted(top_4_harufs)))} ]", language="text")
                        with hc2:
                            st.markdown("🔥 **6-हरूफ़ क्रॉसिंग (Top 6):**")
                            st.code(f"[ {', '.join(map(str, sorted(top_6_harufs)))} ]", language="text")

                        # ---- व्हाट्सएप मैसेज (सिंगल गेम) ----
                        haruf_wa_text = (
                            f"🔥 *ऑटो-सेट केवल हर्फ़ लड़ी रिपोर्ट* 🔥\n\n"
                            f"📍 *गेम:* `{active_g}`\n"
                            f"🗓️️ *ऑटो-सेट लड़ी:* {auto_days} दिन\n"
                            f"📊 *लास्ट पैटर्न:* {recent_nums}\n\n"
                            f"⚡ *4-हरूफ़ क्रॉसिंग:* [{', '.join(map(str, sorted(top_4_harufs)))}]\n"
                            f"🔥 *6-हरूफ़ क्रॉसिंग:* [{', '.join(map(str, sorted(top_6_harufs)))}]\n"
                            f"🎯 *मैचिंग रिज़ल्ट्स:* {box_str}"
                        )
                        
                        encoded_h_wa = urllib.parse.quote(haruf_wa_text)
                        h_wa_url = f"https://api.whatsapp.com/send?text={encoded_h_wa}"

                        st.markdown(
                            f'<a href="{h_wa_url}" target="_blank">'
                            f'<button style="background-color:#25D366; color:white; border:none; padding:10px 16px; '
                            f'font-size:14px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%; margin-top:8px;">'
                            f'📲 {active_g} की हर्फ़ क्रॉसिंग WhatsApp पर शेयर करें'
                            f'</button></a>',
                            unsafe_allow_html=True
                        )

                        st.markdown("---")

                    st.markdown(f"📋 **Next Result - कुल `{len(clean_nums)}` नंबर:**")
                    st.text_area("कॉपी करने के लिए यहाँ क्लिक करें:", value=box_str, height=120, key=f"copy_{k_prefix}_{active_g}_{auto_days}")
                    st.dataframe(match_df, use_container_width=True)
                else:
                    st.warning("⚠️ इस गेम के लिए कोई पुराना रिकॉर्ड मैच नहीं हुआ।")

        # ---- सभी गेम्स की हर्फ़ लड़ी व्हाट्सएप शेयरिंग मास्टर सेक्शन ----
        st.markdown("---")
        st.markdown("### 🚀 सभी गेम्स की ऑटो-सेट हर्फ़ लड़ी रिपोर्ट (WhatsApp Master Share):")
        all_games_h_msgs = []
        for g_name in available_cols:
            if use_manual:
                a_d = manual_days
                m_recs, r_nums = run_fast_sequence_search(df, g_name, available_cols, date_col, "2", a_d)
            else:
                a_d, m_recs, r_nums = find_auto_best_sequence(df, g_name, available_cols, date_col, "2")

            if m_recs:
                n_res = [r["Next Result"] for r in m_recs]
                h_cnts = {d: 0 for d in range(10)}
                for nv in n_res:
                    hi, ho = get_haruf(nv)
                    if hi is not None and 0 <= hi <= 9: h_cnts[hi] += 1
                    if ho is not None and 0 <= ho <= 9: h_cnts[ho] += 1
                srt_h = sorted(h_cnts.keys(), key=lambda d: h_cnts[d], reverse=True)
                top6_h = sorted(srt_h[:6])
                top4_h = sorted(srt_h[:4])
                
                all_games_h_msgs.append(
                    f"📍 *{g_name}* (ऑटो सेट: {a_d} दिन - {r_nums})\n"
                    f"⚡ 4-हरूफ़: [{', '.join(map(str, top4_h))}]\n"
                    f"🔥 6-हरूफ़: [{', '.join(map(str, top6_h))}]"
                )

        if all_games_h_msgs:
            comb_h_wa = f"📊 *ALL GAMES AUTO-SET KEWAL HARUF CROSSING* 📊\n\n" + "\n\n------------------\n\n".join(all_games_h_msgs)
            encoded_comb_h = urllib.parse.quote(comb_h_wa)
            comb_h_wa_url = f"https://api.whatsapp.com/send?text={encoded_comb_h}"

            st.markdown(
                f'<a href="{comb_h_wa_url}" target="_blank">'
                f'<button style="background-color:#075E54; color:white; border:none; padding:12px 18px; '
                f'font-size:15px; border-radius:10px; cursor:pointer; font-weight:bold; width:100%;">'
                f'📲 सभी गेम्स की ऑटो-सेट हर्फ़ क्रॉसिंग WhatsApp पर शेयर करें'
                f'</button></a>',
                unsafe_allow_html=True
            )

    # ================= TAB 2: ANALYZED CROSSING ENGINE =================
    with main_tab2:
        st.subheader("🤖 Top 6 Haruf Crossing Engine (ऑटो शेयरिंग सुविधा के साथ)")

        all_whatsapp_msgs = []

        for col in available_cols:
            vals = df[col].dropna().astype(int).tolist()
            if not vals: continue
            
            last_num = vals[-1]
            top_6_harufs, note = get_statistically_analyzed_crossing(df, col)
            
            if top_6_harufs:
                crossing_str = ", ".join(map(str, top_6_harufs))
                top_3_str = ", ".join(map(str, top_6_harufs[:3]))
            else:
                crossing_str = "N/A"
                top_3_str = "N/A"

            wa_text = (
                f"🔥 *6 HARUF CROSSING REPORT* 🔥\n\n"
                f"📍 *गेम:* `{col}`\n"
                f"🎯 *ताज़ा रिज़ल्ट:* *{last_num:02d}*\n\n"
                f"⚡ *6-हरूफ़ क्रॉसिंग:* [{crossing_str}]\n"
                f"👑 *टॉप 3 मेन हरूफ़:* [{top_3_str}]\n"
                f"📊 *टोटल जोड़ियाँ:* 36 Direct Pairs\n"
                f"💡 _{note}_"
            )
            
            encoded_wa = urllib.parse.quote(wa_text)
            wa_url = f"https://api.whatsapp.com/send?text={encoded_wa}"

            all_whatsapp_msgs.append(wa_text)

            with st.container():
                c1, c2, c3, c4 = st.columns([1.5, 2.5, 2, 2])
                with c1:
                    st.markdown(f"### 📍 {col}")
                    st.caption(f"लास्ट रिज़ल्ट: **{last_num:02d}**")
                with c2:
                    st.markdown(f"🔥 **6-हरूफ़ क्रॉसिंग:** `{crossing_str}`")
                    st.caption(f"👑 **टॉप 3 हरूफ़:** `{top_3_str}`")
                with c3:
                    st.info(f"💡 {note}")
                with c4:
                    st.markdown(
                        f'<a href="{wa_url}" target="_blank">'
                        f'<button style="background-color:#25D366; color:white; border:none; padding:10px 16px; '
                        f'font-size:14px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%; margin-top:8px;">'
                        f'📲 WhatsApp पर शेयर करें'
                        f'</button></a>',
                        unsafe_allow_html=True
                    )
                st.markdown("---")

        if all_whatsapp_msgs:
            combined_all_wa = "📊 *ALL GAMES 6-HARUF CROSSING REPORT* 📊\n\n" + "\n\n------------------\n\n".join(all_whatsapp_msgs)
            encoded_combined = urllib.parse.quote(combined_all_wa)
            comb_wa_url = f"https://api.whatsapp.com/send?text={encoded_combined}"

            st.markdown(
                f'<a href="{comb_wa_url}" target="_blank">'
                f'<button style="background-color:#075E54; color:white; border:none; padding:14px 20px; '
                f'font-size:16px; border-radius:10px; cursor:pointer; font-weight:bold; width:100%;">'
                f'🚀 सभी गेम्स की पूरी 6-हरूफ़ रिपोर्ट एक साथ WhatsApp पर शेयर करें'
                f'</button></a>',
                unsafe_allow_html=True
            )

    # ================= TAB 3: AUTO-DETECT RARE NUMBER 24H SCANNER =================
    with main_tab3:
        st.subheader("⚡ ऑटो-डिटेक्ट रेयर नंबर 24H स्कैनर")
        
        latest_val = df[active_g].dropna().iloc[-1] if not df[active_g].dropna().empty else 20
        auto_detected_num = int(latest_val)
        
        scan_target = st.number_input(f"टारगेट नंबर (ऑटो-डिटेक्टेड: `{auto_detected_num:02d}`):", 0, 99, auto_detected_num, key="scan_target_num_auto_24h")
        
        hist_records_24h = []
        direct_hits = []
        family_hits = []
        location_hits = []

        for col in available_cols:
            col_series = df[col].dropna().reset_index(drop=True)
            for idx in range(len(co
