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
    "आपके बताए गए डिज़ाइन और फॉर्मेट के अनुसार कंबाइंड रिपोर्ट तैयार कर दी गई"
    " है।"
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
    st.subheader("📊 फाइनल अपडेटेड फॉर्मेट रिपोर्ट")


    # Tab 1 Function: Crossing & Haruf
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


    # Tab 2 Function: Single Direct Number
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
      return {"single_direct": f"{best_single_num:02d}"}


    all_unique_harufs = set()
    all_single_numbers = []
    game_data = []

    for col in available_cols:
      res_t1 = analyze_best_crossing_and_haruf(df, col)
      res_t2 = get_best_single_direct_number(df, col)
      if res_t1 and res_t2:
        all_unique_harufs.add(res_t1["single_h_int"])
        all_single_numbers.append(res_t2["single_direct"])
        game_data.append((col, res_t1, res_t2))

    # यूनिक क्रॉसिंग बिना कॉमा के (जैसे 01468)
    sorted_unique = sorted(list(all_unique_harufs))
    unique_crossing_str = "".join(map(str, sorted_unique))

    # सभी सिंगल नंबर और उनकी पलट एक लाइन में बनाने के लिए
    singles_joined = ", ".join(all_single_numbers)
    palat_joined = ", ".join([num[::-1] for num in all_single_numbers])

    whatsapp_blocks = []
    combined_results = []

    for col, res_t1, res_t2 in game_data:
      single_num = res_t2["single_direct"]
      haruf_num = res_t1["single_haruf"]

      combined_results.append({
          "लोकेशन / गेम": col,
          "सिंगल नंबर": f"{single_num} (100)",
          "हरूफ (AB)": f"AB {haruf_num} (250)",
          "क्रॉसिंग": f"{unique_crossing_str} (50)",
      })

      # आपके बताए गए फॉर्मेट के अनुसार हर गेम का ब्लॉक
      block = (
          f"*{col}*\n"
          f"*{single_num}*(100)\n"
          f"*{haruf_num}* AB (250)\n"
          f"*Crossing* {unique_crossing_str}(50)\n\n"
          f"{singles_joined}(100)\n"
          f"{palat_joined}(50)"
      )
      whatsapp_blocks.append(block)

    if combined_results:
      st.dataframe(
          pd.DataFrame(combined_results),
          use_container_width=True,
          hide_index=True,
      )

      st.markdown("---")

      # व्हाट्सएप पर भेजने के लिए संपूर्ण टेक्स्ट
      final_whatsapp_text = (
          f"📅 *Date: {current_date}*\n\n" + "\n\n".join(whatsapp_blocks)
      )
      encoded_msg = urllib.parse.quote(final_whatsapp_text)
      wa_url = f"https://api.whatsapp.com/send?text={encoded_msg}"

      st.markdown(
          f'<a href="{wa_url}" target="_blank">'
          '<button style="background-color:#25D366; color:white;'
          " border:none; padding:12px 20px; "
          "font-size:16px; border-radius:8px; cursor:pointer;"
          ' font-weight:bold; width:100%;">'
          "📲 व्हाट्सएप पर भेजें (Share Report)"
          "</button></a>",
          unsafe_allow_html=True,
      )

  else:
    st.error("CSV फ़ाइल में आवश्यक कॉलम नहीं मिले!")
else:
  st.info("कृपया आगे बढ़ने के लिए अपनी CSV फ़ाइल अपलोड करें।")
                     
