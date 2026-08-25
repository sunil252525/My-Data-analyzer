# Top 3 Single Repeat Numbers निकालें
single_counts = Counter(window_list)
top_3_tuples = single_counts.most_common(3) # (number, count)

# जो 3 सबसे ज्यादा आए हैं, वही लिस्ट बॉक्स में जाएगी
top_3_singles = [item[0] for item in top_3_tuples]
top_3_singles_str = ", ".join([f"{n:02d}" for n in top_3_singles])

# डब्बा 1 का टेक्स्ट एरिया
st.text_area("कॉपी करें (Top 3 Single Repeat Numbers):", value=top_3_singles_str, height=130, key="txt_single_top3")

# नीचे लिस्ट में भी वही 3 नंबर दिखाएँ
st.markdown("**Top 3 नंबरों की फ्रीक्वेंसी:**")
for num, count in top_3_tuples:
    st.write(f"- नंबर **`{num:02d}`**: कुल **{count}** बार आया")
    
