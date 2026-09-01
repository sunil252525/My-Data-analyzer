import streamlit as st
import random

st.set_page_config(page_title="Number Splitter & Combiner", layout="wide")

st.title("नंबर स्प्रेडर, मिक्सर व मल्टी-ग्रुप जनरेटर")

# ---------------- मुख्य सेटिंग्स (लोकेशन व सेट साइज़) ----------------
st.subheader("⚙️ मार्केट व सेटिंग्स")
col_s1, col_s2 = st.columns(2)

with col_s1:
    market_tag = st.text_input(
        "मार्केट / लोकेशन दर्ज करें (उदा. FB, GB, GL, DS):", 
        value="GB",
        placeholder="यहाँ टाइप करें (उदा. FB, GB, GL, DS)..."
    )

with col_s2:
    chunk_choice = st.selectbox(
        "एक लाइन में कितने नंबर रखें?", 
        options=[4, 5, 6, 7], 
        index=1
    )

st.divider()

# ---------------- इनपुट सेक्शन ----------------
col_inp1, col_inp2 = st.columns(2)

with col_inp1:
    st.subheader("📋 ग्रुप नंबर इनपुट")
    input_ab = st.text_area(
        "1. ग्रुप A और B के लिए नंबर (कॉमा लगाकर):", 
        placeholder="00, 01, 02, 03...", 
        height=100
    )
    input_cd = st.text_area(
        "2. ग्रुप C और D के लिए नंबर (कॉमा लगाकर):", 
        placeholder="04, 05, 06, 07...", 
        height=100
    )

with col_inp2:
    st.subheader("🔀 नंबर मिक्सर (क्रॉस क्रॉस/जोड़ी जनरेटर)")
    input_mix_1 = st.text_input(
        "पहला सेट दर्ज करें (उदा. 6 नंबर):", 
        placeholder="7, 8, 9, 0, 1, 2"
    )
    input_mix_2 = st.text_input(
        "दूसरा सेट दर्ज करें (उदा. 3-4 नंबर):", 
        placeholder="1, 2, 3, 4"
    )

st.divider()

# ---------------- जनरेट बटन व लॉजिक ----------------
if st.button("जनरेट करें (Generate)", type="primary"):
    tag_str = f" {market_tag.strip()}" if market_tag.strip() else ""

    # 1. ग्रुप A और B प्रोसेसिंग
    nums_ab = [n.strip() for n in input_ab.split(',') if n.strip()]
    random.shuffle(nums_ab)
    half_ab = len(nums_ab) // 2
    group_a = nums_ab[:half_ab]
    group_b = nums_ab[half_ab:]
    
    # 2. ग्रुप C और D प्रोसेसिंग
    nums_cd = [n.strip() for n in input_cd.split(',') if n.strip()]
    random.shuffle(nums_cd)
    half_cd = len(nums_cd) // 2
    group_c = nums_cd[:half_cd]
    group_d = nums_cd[half_cd:]

    # 3. क्रॉस मिक्सर लॉजिक (उदा. '7' और '1' मिलकर '71')
    set1 = [n.strip() for n in input_mix_1.split(',') if n.strip()]
    set2 = [n.strip() for n in input_mix_2.split(',') if n.strip()]
    mixed_pairs = [f"{n1}{n2}" for n1 in set1 for n2 in set2]
    
    # 4. मुख्य चार ग्रुप का डिस्प्ले
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
                
                # चुने गए टुकड़े (4, 5, 6, 7) में बाँटना
                sub_groups = [data[i:i + chunk_choice] for i in range(0, len(data), chunk_choice)]
                
                # बिना सीरियल नंबर (1., 2.) के सीधा टेक्स्ट दिखाना
                for sub_data in sub_groups:
                    formatted_line = sep.join(sub_data) + f" {rate}"
                    st.text(formatted_line)

    # 5. मिक्सर ग्रुप का डिस्प्ले (अगर नंबर डाले गए हों)
    if mixed_pairs:
        st.divider()
        st.subheader(f"🔗 मिक्सर से बने नंबर / Cross Combined ({len(mixed_pairs)} नंबर)")
        st.success(", ".join(mixed_pairs))
        
        mix_sub_groups = [mixed_pairs[i:i + chunk_choice] for i in range(0, len(mixed_pairs), chunk_choice)]
        
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.markdown("**स्लैश (`/`) सेपरेटर के साथ:**")
            for sub_data in mix_sub_groups:
                formatted_line = " / ".join(sub_data) + f" (100){tag_str}"
                st.text(formatted_line)
                
        with col_m2:
            st.markdown("**डैश (`-`) सेपरेटर के साथ:**")
            for sub_data in mix_sub_groups:
                formatted_line = " - ".join(sub_data) + f" (100){tag_str}"
                st.text(formatted_line)
