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
    "यहाँ दो टैब दिए गए हैं: पहला **क्रॉसिंग इंजन** के लिए और दूसरा **सिंगल"
    " डायरेक्ट नंबर इंजन** के लिए।"
)

# --- FILE UPLOADER (SHARED FOR BOTH TABS) ---
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
        top_6_harufs = sorted(ranked_harufs[:6])

        return {
            "single_haruf": str(single_haruf),
            "haruf_6_str": ", ".join(map(str, top_6_harufs)),
            "single_h_int": single_haruf,
        }


      analysis_results = []
      all_unique_harufs = set()

      # पहले सभी गेम्स के सिंगल हरूफ़ एकत्र करें ताकि यूनिक क्रॉसिंग बन सके
      temp_game_data = []
      for col in available_cols:
        res = analyze_best_crossing_and_haruf(df, col)
        if res:
          temp_game_data.append((col, res))
          all_unique_harufs.add(res["single_h_int"])

      sorted_unique = sorted(list(all_unique_harufs))
      unique_crossing_str = ", ".join(map(str, sorted_unique))

      wa_msg_lines = []
      for col, res in temp_game_data:
        analysis_results.append({
            "लोकेशन / गेम": col,
            "सिंगल हरूफ़": res["single_haruf"],
            "क्रॉसिंग": res["haruf_6_str"],
        })

        # हर गेम के ब्लॉक में: नाम, सिंगल हरूफ़, गेम की क्रॉसिंग, और सबसे नीचे उस गेम के साथ यूनिक क्रॉसिंग
        game_msg = (
            f"*{col}*\n*{res['single_haruf']}*\n[{res['haruf_6_str']}]\n["
            f"{unique_crossing_str}]"
        )
        wa_msg_lines.append(game_msg)

      if analysis_results:
        st.dataframe(
            pd.DataFrame(analysis_results),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown(
            "### 🔗 सभी गेम के सिंगल हरूफ़ की संयुक्त क्रॉसिंग (Unique Harufs"
            " Crossing)"
        )
        st.code(unique_crossing_str, language="text")

        st.markdown("---")

        # सबसे ऊपर डेट और फिर सभी गेम्स के साथ यूनिक क्रॉसिंग फॉर्मेट
        clean_whatsapp_text = (
            f"📅 *Date: {current_date}*\n\n" + "\n\n".join(wa_msg_lines)
        )
        encoded_full_msg = urllib.parse.quote(clean_whatsapp_text)
        wa_full_url = f"https://api.whatsapp.com/send?text={encoded_full_msg}"

        st.markdown(
            f'<a href="{wa_full_url}" target="_blank">'
            '<button style="background-color:#25D366; color:white;'
            " border:none; padding:12px 20px; "
            "font-size:16px; border-radius:8px; cursor:pointer;"
            ' font-weight:bold; width:100%;">'
            "📲 क्रॉसिंग बॉक्स WhatsApp पर भेजें (Share Clean Box)"
            "</button></a>",
            unsafe_allow_html=True,
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
            "single_direct": f"{best_single_num:02d}",
            "score": round(num_scores[best_single_num], 1),
        }


      single_results = []
      wa_msg_lines_single = []

      for col in available_cols:
        res = get_best_single_direct_number(df, col)
        if res:
          single_results.append({
              "लोकेशन / गेम": col,
              "सिंगल नंबर": res["single_direct"],
              "स्कोर": f"{res['score']} pts",
          })
          wa_msg_lines_single.append(f"*{col}*\n*{res['single_direct']}*")

      if single_results:
        st.dataframe(
            pd.DataFrame(single_results),
            use_container_width=True,
            hide_index=True,
        )

        wa_text = (
            f"📅 *Date: {current_date}*\n\n" + "\n\n".join(wa_msg_lines_single)
        )
        encoded_msg = urllib.parse.quote(wa_text)
        wa_url = f"https://api.whatsapp.com/send?text={encoded_msg}"

        st.markdown(
            f'<a href="{wa_url}" target="_blank">'
            '<button style="background-color:#25D366; color:white;'
            " border:none; padding:12px 20px; "
            "font-size:16px; border-radius:8px; cursor:pointer;"
            ' font-weight:bold; width:100%;">'
            "📲 केवल सिंगल नंबर WhatsApp पर भेजें (Share Single Numbers)"
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
            
