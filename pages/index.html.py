import streamlit as st
import random

st.set_page_config(page_title="Number Splitter & Combiner", layout="wide")

st.title("नंबर स्प्रेडर, मिक्सर व मल्टी-ग्रुप जनरेटर")

# साइडबार - लोकेशन/टैग और सेट साइज की सेटिंग
st.sidebar.header("⚙️ अतिरिक्त सेटिंग्स")
location_tag = st.sidebar.text_input("मार्केट/लोकेशन कोड (उदा. GB, DB, FB):", value="GB")
chunk_choice = st.sidebar.selectbox("एक लाइन में कितने नंबर रखें?", options=[4, 5, 6, 7], index=1)

# मुख्य इनपुट सेक्शन
col_inp1, col_inp2 = st.columns(2)

with col_inp1:
    input_ab = st.text_area(
        "1. यहाँ ग्रुप A और B के लिए नंबर दर्ज करें (कॉमा लगाकर):", 
        placeholder="00, 01, 02, 03...", 
        height=100
    )
    input_cd = st.text_area(
        "2. यहाँ ग्रुप C और D के लिए नंबर दर्ज करें (कॉमा लगाकर):", 
        placeholder="04, 05, 06, 07...", 
        height=100
    )

with col_inp2:
    st.subheader("🔀 नंबर मिक्सर (Cross Combine)")
    input_mix_1 = st.text_input("6 नंबर का सेट दर्ज करें:", placeholder="01, 02, 03, 04, 05, 06")
    input_mix_2 = st.text_input("3-4 नंबर का सेट दर्ज करें:", placeholder="07, 08, 09, 00")

if st.button("जनरेट करें (Generate)", type="primary"):
    tag_str = f" {location_tag.strip()}" if location_tag.strip() else ""

    # 1. ग्रुप A और B
    nums_ab = [n.strip() for n in input_ab.split(',') if n.strip()]
    random.shuffle(nums_ab)
    half_ab = len(nums_ab) // 2
    group_a = nums_ab[:half_ab]
    group_b = nums_ab[half_ab:]
    
    # 2. ग्रुप C और D
    nums_cd = [n.strip() for n in input_cd.split(',') if n.strip()]
    random.shuffle(nums_cd)
    half_cd = len(nums_cd) // 2
    group_c = nums_cd[:half_cd]
    group_d = nums_cd[half_cd:]

    # 3. क्रॉस मिक्सर ग्रुप (Cross Combining logic)
    set1 = [n.strip() for n in input_mix_1.split(',') if n.strip()]
    set2 = [n.strip() for n in input_mix_2.split(',') if n.strip()]
    mixed_pairs = [f"{n1}{n2}" for n1 in set1 for n2 in set2]
    
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
                
                # कस्टम टुकड़ों (4, 5, 6, 7) में बाँटना
                sub_groups = [data[i:i + chunk_choice] for i in range(0, len(data), chunk_choice)]
                
                # बिना 1., 2. के सीधा-सीधा प्रिंट करना
                for sub_data in sub_groups:
                    formatted_line = sep.join(sub_data) + f" {rate}"
                    st.text(formatted_line)

    # अगर मिक्सर में नंबर डाले गए हैं तो अलग सेक्शन में दिखाएं
    if mixed_pairs:
        st.divider()
        st.subheader(f"🔗 मिक्सर ग्रुप / Cross Combined ({len(mixed_pairs)} नंबर)")
        st.success(", ".join(mixed_pairs))
        
        mix_sub_groups = [mixed_pairs[i:i + chunk_choice] for i in range(0, len(mixed_pairs), chunk_choice)]
        for sub_data in mix_sub_groups:
            formatted_line = " / ".join(sub_data) + f" (100){tag_str}"
            st.text(formatted_line)
