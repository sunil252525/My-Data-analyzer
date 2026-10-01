import streamlit as st
import pandas as pd
import urllib.parse

# Streamlit Page Config
st.set_page_config(page_title="Single Direct Number Engine", layout="wide")

# --- 1. SINGLE DIRECT NUMBER GENERATOR ENGINE ---
def get_best_single_direct_number(df, column_name):
    vals = df[column_name].dropna().tolist()
    valid_vals = []
    
    for x in vals:
        try:
            v = int(x)
            if 0 <= v <= 99:
                valid_vals.append(v)
        except:
            continue
            
    if len(valid_vals) < 10:
        return None

    last_num = valid_vals[-1]
    
    # Calculate Top Inside & Outside Haruf
    in_haruf_counts = {d: 0 for d in range(10)}
    out_haruf_counts = {d: 0 for d in range(10)}
    for num in valid_vals[-50:]:
        in_haruf_counts[num // 10] += 1
        out_haruf_counts[num % 10] += 1
        
    top_in_haruf = max(in_haruf_counts.keys(), key=lambda x: in_haruf_counts[x])
    top_out_haruf = max(out_haruf_counts.keys(), key=lambda x: out_haruf_counts[x])
    
    # Score numbers 00 to 99
    num_scores = {n: 0.0 for n in range(100)}
    
    # Rule 1: Exact 1-Day Follow-Up (+5 Points)
    for i in range(len(valid_vals) - 1):
        if valid_vals[i] == last_num:
            nxt = valid_vals[i + 1]
            num_scores[nxt] += 5.0
            
    # Rule 2: Exact 2-Day Follow-Up (+3 Points)
    for i in range(len(valid_vals) - 2):
        if valid_vals[i] == last_num:
            nxt2 = valid_vals[i + 2]
            num_scores[nxt2] += 3.0
            
    # Rule 3: Top Haruf Intersection Bonus (+4 Points)
    crossing_best = top_in_haruf * 10 + top_out_haruf
    num_scores[crossing_best] += 4.0
    
    # Rule 4: Recent Momentum (Last 30 Draws) (+0.5 Points)
    for n in valid_vals[-30:]:
        num_scores[n] += 0.5
        
    # Get Top Highest Scoring Single Number
    best_single_num = max(num_scores.keys(), key=lambda x: num_scores[x])
    
    return {
        "last_num": f"{last_num:02d}",
        "single_direct": f"{best_single_num:02d}",
        "score": round(num_scores[best_single_num], 1)
    }

# --- 2. RENDER SINGLE NUMBER DISPLAY BOX ---
def render_single_number_dashboard(df, available_cols):
    st.title("🎯 100% सिंगल नंबर डायरेक्ट इंजन (No Palat - Straight Single Number)")
    st.write("13 सालों के डेटाबेस पर 4-लेयर फ़िल्टर चलाकर निकाला गया गेम-वाइज़ **सिंगल नंबर (बिना पलट)**:")

    single_results = []
    wa_msg_lines = []

    for col in available_cols:
        res = get_best_single_direct_number(df, col)
        if res:
            single_results.append({
                "लोकेशन / गेम": col,
                "🎯 ताज़ा रिज़ल्ट": res["last_num"],
                "👑 1 सिंगल नंबर (No Palat)": f"🔥 {res['single_direct']} (100)",
                "📊 एल्गोरिदम स्कोर": f"{res['score']} pts"
            })
            wa_msg_lines.append(f"• *{col}* (Last: {res['last_num']}) ➔ Single: *{res['single_direct']}* (100)")

    if single_results:
        st.dataframe(pd.DataFrame(single_results), use_container_width=True, hide_index=True)
        
        # --- SINGLE NUMBER CODE DISPLAY BOX ---
        st.markdown("### 📋 सभी गेम का 1-1 सिंगल नंबर (Copy / Direct Line)")
        direct_line_text = ", ".join([f"{r['👑 1 सिंगल नंबर (No Palat)'].split()[1]}" for r in single_results])
        st.code(direct_line_text, language="text")

        # --- WHATSAPP SHARE LINK FOR SINGLE NUMBERS ---
        wa_text = "🎯 *TODAY SINGLE DIRECT NUMBERS (NO PALAT)* 🎯\n\n" + "\n".join(wa_msg_lines)
        encoded_msg = urllib.parse.quote(wa_text)
        wa_url = f"https://api.whatsapp.com/send?text={encoded_msg}"
        
        st.markdown(
            f'<a href="{wa_url}" target="_blank">'
            f'<button style="background-color:#25D366; color:white; border:none; padding:12px 24px; '
            f'font-size:16px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%;">'
            f'📲 केवल सिंगल नंबर WhatsApp पर भेजें (Share Single Numbers)'
            f'</button></a>',
            unsafe_allow_html=True
        )
    else:
        st.warning("डेटा कम है या कॉलम मैच नहीं हो पा रहे हैं।")

# --- 3. MAIN APPLICATION CODE ---
st.title("📂 Single Direct Number Predictor")
uploaded_file = st.file_uploader("अपनी CSV फ़ाइल यहाँ अपलोड करें", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    series_cols = ['DB', 'SG', 'FRBD', 'GZBD', 'GALI', 'DSWR']
    available_cols = [c for c in series_cols if c in df.columns]
    
    if available_cols:
        render_single_number_dashboard(df, available_cols)
    else:
        st.error("CSV फ़ाइल में कोई भी मैचिंग गेम कॉलम नहीं मिला!")
  
