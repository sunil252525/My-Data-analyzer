import streamlit as st
import random

st.set_page_config(page_title="Number Splitter & Combiner", layout="wide")

st.title("नंबर स्प्रेडर, मिक्सर व मल्टी-ग्रुप जनरेटर")

# ---------------- मुख्य सेटिंग्स ----------------
st.subheader("⚙️ मार्केट व सेटिंग्स")
col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    market_tag = st.text_input(
        "मार्केट / लोकेशन दर्ज करें (उदा. FB, GB, GL, DS):", 
        value="Gali",
        placeholder="यहाँ टाइप करें..."
    )

with col_s2:
    chunk_choice = st.selectbox(
        "एक लाइन में कितने नंबर रखें?", 
        options=[4, 5, 6, 7], 
        index=2
    )

with col_s3:
    split_ab = st.checkbox("बॉक्स 1 के नंबर A और B में आधे-आधे बाँटें", value=False)

st.divider()

# ---------------- इनपुट सेक्शन ----------------
col_inp1, col_inp2 = st.columns(2)

with col_inp1:
    st.subheader("📋 ग्रुप नंबर इनपुट")
    input_ab = st.text_area(
        "1. ग्रुप A के लिए नंबर (कॉमा लगाकर):", 
        placeholder="04, 25, 02, 05, 13, 01, 24...", 
        height=100
    )
    input_cd = st.text_area(
        "2. ग्रुप C और D के लिए नंबर (कॉमा लगाकर):", 
        placeholder="04, 05, 06, 07...", 
        height=100
    )

with col_inp2:
    st.subheader("🔀 नंबर मिक्सर (क्रॉस/जोड़ी जनरेटर)")
    input_mix_1 = st.text_input(
        "पहला सेट (बिना कॉमा या कॉमा लगाकर):", 
        placeholder="7890 या 7,8,9,0"
    )
    input_mix_2 = st.text_input(
        "दूसरा सेट (बिना कॉमा या कॉमा लगाकर):", 
        placeholder="123456 या 1,2,3,4,5,6"
    )

st.divider()

# ---------------- जनरेट बटन व लॉजिक ----------------
if st.button("जनरेट करें (Generate)", type="primary"):
    tag_str = f" {market_tag.strip()}" if market_tag.strip() else ""

    # 1. बॉक्स 1 प्रोसेसिंग (A और B)
    nums_ab = [n.strip() for n in input_ab.split(',') if n.strip()]
    if split_ab and len(nums_ab) > 1:
        random.shuffle(nums_ab)
        half_ab = len(nums_ab) // 2
        group_a = nums_ab[:half_ab]
        group_b = nums_ab[half_ab:]
    else:
        group_a = nums_ab
        group_b = []

    # 2. बॉक्स 2 प्रोसेसिंग (C और D)
    nums_cd = [n.strip() for n in input_cd.split(',') if n.strip()]
    if nums_cd:
        random.shuffle(nums_cd)
        half_cd = len(nums_cd) // 2
        group_c = nums_cd[:half_cd]
        group_d = nums_cd[half_cd:]
    else:
        group_c = []
        group_d = []

    # 3. बिना कॉमा / कॉमा दोनों के लिए ऑटो-डिटेक्ट लॉजिक
    def parse_digits(raw_str):
        raw_str = raw_str.strip()
        if ',' in raw_str:
            return [n.strip() for n in raw_str.split(',') if n.strip()]
        else:
            return [ch for ch in raw_str if ch.strip()]

    set1 = parse_digits(input_mix_1)
    set2 = parse_digits(input_mix_2)
    
    mixed_straight = []
    mixed_reverse = []
    
    if set1 and set2:
        for d1 in set1:
            for d2 in set2:
                mixed_straight.append(f"{d1}{d2}")
                mixed_reverse.append(f"{d2}{d1}") # पलटी
    
    # 4. मुख्य चार ग्रुप का प्रदर्शन
    groups = [
        {"name": f"ग्रुप A ({len(group_a)} नंबर)", "data": group_a, "sep": " / ", "rate": f"(100){tag_str}"},
        {"name": f"ग्रुप B ({len(group_b)} नंबर)", "data": group_b, "sep": " - ", "rate": f"(95){tag_str}"},
        {"name": f"ग्रुप C ({len(group_c)} नंबर)", "data": group_c, "sep": " _ ", "rate": f"(90){tag_str}"},
        {"name": f"ग्रुप D ({len(group_d)} नंबर)", "data": group_d, "sep": " . ", "rate": f"(50){tag_str}"}
    ]
    
    cols = st.columns(4)
    for idx, grp in enumerate(groups):
        with cols[idx]:
            st.subheader(grp["name"])
            if grp["data"]:
                st.info(", ".join(grp["data"]))
                sep = grp["sep"]
                rate = grp["rate"]
                data = grp["data"]
                
                sub_groups = [data[i:i + chunk_choice] for i in range(0, len(data), chunk_choice)]
                for sub_data in sub_groups:
                    formatted_line = sep.join(sub_data) + f" {rate}"
                    st.text(formatted_line)

    # 5. मिक्सर रिजल्ट (4 स्टाइल: सीधा, सीधा मिक्स, पलटी, पलटी मिक्स)
    if mixed_straight:
        st.divider()
        st.subheader(f"🔗 मिक्सर से बनी जोड़ियाँ ({len(mixed_straight)} नंबर)")
        st.success(", ".join(mixed_straight))
        
        # मिक्स/शफल वर्ज़न तैयार करना
        straight_shuffled = mixed_straight.copy()
        random.shuffle(straight_shuffled)
        
        reverse_shuffled = mixed_reverse.copy()
        random.shuffle(reverse_shuffled)

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        # कॉलम 1: सीधा (सीरियल) /
        with col_m1:
            st.markdown("**1. सीधे (सीरियल वाइज) `/` :**")
            sub_groups = [mixed_straight[i:i + chunk_choice] for i in range(0, len(mixed_straight), chunk_choice)]
            for sub_data in sub_groups:
                st.text(" / ".join(sub_data) + f" (100){tag_str}")
                
        # कॉलम 2: सीधा (मिक्स) -
        with col_m2:
            st.markdown("**2. सीधे (रैंडम/मिक्स) `-` :**")
            sub_groups = [straight_shuffled[i:i + chunk_choice] for i in range(0, len(straight_shuffled), chunk_choice)]
            for sub_data in sub_groups:
                st.text(" - ".join(sub_data) + f" (100){tag_str}")

        # कॉलम 3: पलटी (सीरियल) -
        with col_m3:
            st.markdown("**3. पलटी (सीरियल वाइज) `-` :**")
            sub_groups = [mixed_reverse[i:i + chunk_choice] for i in range(0, len(mixed_reverse), chunk_choice)]
            for sub_data in sub_groups:
                st.text(" - ".join(sub_data) + f" (100){tag_str}")

        # कॉलम 4: पलटी (मिक्स) /
        with col_m4:
            st.markdown("**4. पलटी (रैंडम/मिक्स) `/` :**")
            sub_groups = [reverse_shuffled[i:i + chunk_choice] for i in range(0, len(reverse_shuffled), chunk_choice)]
            for sub_data in sub_groups:
                st.text(" / ".join(sub_data) + f" (100){tag_str}")
