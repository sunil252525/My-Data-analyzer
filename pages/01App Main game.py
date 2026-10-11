import datetime
import urllib.parse
import pandas as pd
import streamlit as st

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="Advanced All-in-One Analytics & Dashboard", layout="wide"
)

st.title("🎯 All-in-One Game Analytics & Dashboard")
st.write(
    "यहाँ डैशबोर्ड में डेटा टेबल्स अपने पुराने फॉर्मेट में दिखेंगी, और व्हाट्सएप"
    " शेयरिंग आपके बताए गए नए फॉर्मेट में होगी।"
)

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader(
    "📂 कृपया अपनी CSV फ़ाइल यहाँ अपलोड करें", type=["csv"]
)

if uploaded_file is not None:
  df = pd.read_csv(uploaded_file)
  df.columns = df.columns.str.strip()

  # तारीख (Date) खोजने का प्रयास
  date_col = next(
      (
          c
          for c in df.columns
          if "date" in c.lower()
          or "दिनांक" in c
          or "तारीख" in c
          or "tariikh" in c.lower()
      ),
      None,
  )
  if date_col:
    current_date = str(df[date_col].iloc[-1]).strip()
  else:
    current_date = datetime.datetime.now().strftime("%d/%m/%Y")

  series_cols = ["DB", "SG", "FRBD", "GZBD", "GALI", "DSWR"]
  available_cols = [c for c in series_cols if c in df.columns]

  if available_cols:
    tab1, tab2 = st.tabs([
        "🎯 1. Complete Crossing & Haruf Engine",
        "🔥 2. Single Direct Number Engine (No Palat)",
    ])

    # ==========================================
    # TAB 1: COMPLETE CROSSING & HARUF ENGINE
    # ==========================================
    with tab1:
      st.subheader("📊 ऐतिहासिक डेटा और फॉलो-अप पैटर्न के आधार पर क्रॉसिंग")


      def analyze_best_crossing_and_haruf(df, column_name):
        vals = df[column_name].dropna().tolist()
        valid_vals = []
        for x in vals:
          try:
            val = int(x)
            if 0 <= val <= 99:
              valid_vals.append(val)
          except:
            continue
        if len(valid_vals) < 5:
          return None

        last_num = valid_vals[-1]
        haruf_scores = {d: 0 for d in range(10)}
        total_len = len(valid_vals)
        for idx, num in enumerate(valid_vals):
          weight = 1 + (idx / total_len)
          haruf_scores[num // 10] += weight
          haruf_scores[num % 10] += weight

        follow_up_harufs = []
        for i in range(len(valid_vals) - 2):
          if valid_vals[i] == last_num:
            f1 = valid_vals[i + 1]
            f2 = valid_vals[i + 2]
            follow_up_harufs.extend([f1 // 10, f1 % 10, f2 // 10, f2 % 10])

        for h in follow_up_harufs:
          if 0 <= h <= 9:
            haruf_scores[h] += 3.5

        ranked_harufs = sorted(
            haruf_scores.keys(), key=lambda x: haruf_scores[x], reverse=True
        )
        single_haruf = ranked_harufs[0]
        top_4_harufs = sorted(ranked_harufs[:4])
        top_6_harufs = sorted(ranked_harufs[:6])

        return {
            "last_num": f"{last_num:02d}",
            "single_haruf": str(single_haruf),
            "haruf_4_str": ", ".join(map(str, top_4_harufs)),
            "haruf_6_str": ", ".join(map(str, top_6_harufs)),
            "single_h_int": single_haruf,
        }


      analysis_results = []
      for col in available_cols:
        res = analyze_best_crossing_and_haruf(df, col)
        if res:
          analysis_results.append({
              "लोकेशन / गेम": col,
              "🎯 ताज़ा रिज़ल्ट": res["last_num"],
              "👑 सिंगल हरूफ़ (1 Haruf)": (
                  f"🔥 {res['single_haruf']} (अंदर/बाहर)"
              ),
              "⚡ 4 हरूफ़ क्रॉसिंग": res["haruf_4_str"],
              "🔥 6 हरूफ़ क्रॉसिंग": res["haruf_6_str"],
          })

      if analysis_results:
        st.dataframe(
            pd.DataFrame(analysis_results),
            use_container_width=True,
            hide_index=True,
        )

    # ==========================================
    # TAB 2: SINGLE DIRECT NUMBER ENGINE
    # ==========================================
    with tab2:
      st.subheader("🎯 100% सिंगल नंबर डायरेक्ट इंजन (No Palat)")


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
        in_haruf_counts = {d: 0 for d in range(10)}
        out_haruf_counts = {d: 0 for d in range(10)}
        for num in valid_vals[-50:]:
          in_haruf_counts[num // 10] += 1
          out_haruf_counts[num % 10] += 1

        top_in_haruf = max(
            in_haruf_counts.keys(), key=lambda x: in_haruf_counts[x]
        )
        top_out_haruf = max(
            out_haruf_counts.keys(), key=lambda x: out_haruf_counts[x]
        )

        num_scores = {n: 0.0 for n in range(100)}
        for i in range(len(valid_vals) - 1):
          if valid_vals[i] == last_num:
            nxt = valid_vals[i + 1]
            num_scores[nxt] += 5.0

        for i in range(len(valid_vals) - 2):
          if valid_vals[i] == last_num:
            nxt2 = valid_vals[i + 2]
            num_scores[nxt2] += 3.0

        crossing_best = top_in_haruf * 10 + top_out_haruf
        num_scores[crossing_best] += 4.0

        for n in valid_vals[-30:]:
          num_scores[n] += 0.5

        best_single_num = max(num_scores.keys(), key=lambda x: num_scores[x])
        return {
            "last_num": f"{last_num:02d}",
            "single_direct": f"{best_single_num:02d}",
            "score": round(num_scores[best_single_num], 1),
        }


      single_results = []
      for col in available_cols:
        res = get_best_single_direct_number(df, col)
        if res:
          single_results.append({
              "लोकेशन / गेम": col,
              "🎯 ताज़ा रिज़ल्ट": res["last_num"],
              "👑 1 सिंगल नंबर (No Palat)": f"🔥 {res['single_direct']} (100)",
              "📊 एल्गोरिथम स्कोर": f"{res['score']} pts",
          })

      if single_results:
        st.dataframe(
            pd.DataFrame(single_results),
            use_container_width=True,
            hide_index=True,
        )

    # ==========================================
    # WHATSAPP SHARE SECTION (कस्टम फॉर्मेट के साथ)
    # ==========================================
    st.markdown("---")
    st.subheader("📲 WhatsApp शेयरिंग बटन")


    def analyze_for_wa(df, column_name):
      vals = df[column_name].dropna().tolist()
      valid_vals = [int(x) for x in vals if str(x).isdigit() and 0 <= int(x) <= 99]
      if len(valid_vals) < 5:
        return None
      last_num = valid_vals[-1]
      haruf_scores = {d: 0 for d in range(10)}
      for idx, num in enumerate(valid_vals):
        weight = 1 + (idx / len(valid_vals))
        haruf_scores[num // 10] += weight
        haruf_scores[num % 10] += weight
      ranked = sorted(
          haruf_scores.keys(), key=lambda x: haruf_scores[x], reverse=True
      )
      return {"single_haruf": str(ranked[0]), "single_h_int": ranked[0]}


    def single_for_wa(df, column_name):
      vals = df[column_name].dropna().tolist()
      valid_vals = [int(x) for x in vals if str(x).isdigit() and 0 <= int(x) <= 99]
      if len(valid_vals) < 10:
        return None
      last_num = valid_vals[-1]
      in_h = {d: 0 for d in range(10)}
      out_h = {d: 0 for d in range(10)}
      for num in valid_vals[-50:]:
        in_h[num // 10] += 1
        out_h[num % 10] += 1
      top_in = max(in_h, key=in_h.get)
      top_out = max(out_h, key=out_h.get)
      scores = {n: 0.0 for n in range(100)}
      for i in range(len(valid_vals) - 1):
        if valid_vals[i] == last_num:
          scores[valid_vals[i + 1]] += 5.0
      scores[top_in * 10 + top_out] += 4.0
      best_num = max(scores, key=scores.get)
      return f"{best_num:02d}"


    all_unique_harufs = set()
    all_single_numbers = []
    whatsapp_blocks = []

    for col in available_cols:
      res_cross = analyze_for_wa(df, col)
      single_num = single_for_wa(df, col)
      if res_cross and single_num:
        all_unique_harufs.add(res_cross["single_h_int"])
        all_single_numbers.append(single_num)

        haruf_num = res_cross["single_haruf"]
        block = (
            f"*{col}*\n"
            f"*{single_num}*(100)\n"
            f"*{haruf_num}* AB (250)\n"
            f"*Crossing* (50)"
        )
        whatsapp_blocks.append(block)

    sorted_unique = sorted(list(all_unique_harufs))
    unique_crossing_str = "".join(map(str, sorted_unique))

    singles_joined = ", ".join(all_single_numbers)
    palat_joined = ", ".join([num[::-1] for num in all_single_numbers])

    # व्हाट्सएप मैसेज का पूरा ढांचा आपके बताए अनुसार
    final_whatsapp_text = (
        f"📅 *Date: {current_date}*\n\n"
        + f"\n\n".join(whatsapp_blocks)
        + f"\n\n*Crossing* {unique_crossing_str}(50)\n\n"
        + f"{singles_joined}(100)\n"
        + f"{palat_joined}(50)"
    )

    encoded_msg = urllib.parse.quote(final_whatsapp_text)
    wa_url = f"https://api.whatsapp.com/send?text={encoded_msg}"

    st.markdown(
        f'<a href="{wa_url}" target="_blank">'
        '<button style="background-color:#25D366; color:white;'
        " border:none; padding:12px 20px; "
        "font-size:16px; border-radius:8px; cursor:pointer;"
        ' font-weight:bold; width:100%;">'
        "📲 कंबाइंड रिपोर्ट WhatsApp पर भेजें (Share Report)"
        "</button></a>",
        unsafe_allow_html=True,
    )

  else:
    st.error(
        "CSV फ़ाइल में DB, SG, FRBD, GZBD, GALI, DSWR में से कोई भी कॉलम नहीं"
        " मिला!"
    )
else:
  st.info("कृपया आगे बढ़ने के लिए ऊपर दी गई जगह पर अपनी CSV फ़ाइल अपलोड करें।")
          
