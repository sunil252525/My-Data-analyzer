import streamlit as st
import random

st.set_page_config(page_title="Number Splitter App", layout="wide")

st.title("नंबर स्प्रेडर व मल्टी-ग्रुप जनरेटर")

# दो इनपुट बॉक्स
input_ab = st.text_area(
    "1. यहाँ ग्रुप A और B के लिए नंबर दर्ज करें (कॉमा लगाकर):", 
    placeholder="00, 01, 02, 03...", 
    height=120
)

input_cd = st.text_area(
    "2. यहाँ ग्रुप C और D के लिए नंबर दर्ज करें (कॉमा लगाकर):", 
    placeholder="04, 05, 06, 07...", 
    height=120
)

if st.button("जनरेट करें (Generate)", type="primary"):
    if not input_ab.strip() and not input_cd.strip():
        st.warning("कृपया कम से कम एक बॉक्स में नंबर दर्ज करें!")
    else:
        # 1. ग्रुप A और B के नंबर प्रोसेस करें
        nums_ab = [n.strip() for n in input_ab.split(',') if n.strip()]
        random.shuffle(nums_ab)
        half_ab = len(nums_ab) // 2
        group_a = nums_ab[:half_ab]
        group_b = nums_ab[half_ab:]
        
        # 2. ग्रुप C और D के नंबर प्रोसेस करें
        nums_cd = [n.strip() for n in input_cd.split(',') if n.strip()]
        random.shuffle(nums_cd)
        half_cd = len(nums_cd) // 2
        group_c = nums_cd[:half_cd]
        group_d = nums_cd[half_cd:]
        
        # ग्रुप सेटिंग्स
        groups = [
            {"name": f"ग्रुप A ({len(group_a)} नंबर)", "data": group_a, "sep": " / ", "rate": "(100)"},
            {"name": f"ग्रुप B ({len(group_b)} नंबर)", "data": group_b, "sep": " - ", "rate": "(95)"},
            {"name": f"ग्रुप C ({len(group_c)} नंबर)", "data": group_c, "sep": " _ ", "rate": "(90)"},
            {"name": f"ग्रुप D ({len(group_d)} नंबर)", "data": group_d, "sep": " . ", "rate": "(80)"}
        ]
        
        cols = st.columns(4)
        
        for idx, grp in enumerate(groups):
            with cols[idx]:
                st.subheader(grp["name"])
                if grp["data"]:
                    # मुख्य लिस्ट
                    st.info(", ".join(grp["data"]))
                    
                    sep = grp["sep"]
                    rate = grp["rate"]
                    data = grp["data"]
                    
                    # 5-5 के सब-ग्रुप की पंक्तियाँ बनाना
                    chunk_size = 5
                    sub_groups = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
                    
                    for sub_idx, sub_data in enumerate(sub_groups, 1):
                        formatted_line = sep.join(sub_data) + f" {rate}"
                        st.write(f"**{sub_idx}.** {formatted_line}")
