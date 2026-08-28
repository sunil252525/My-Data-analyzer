import streamlit as st
import random

st.set_page_config(page_title="Number Splitter App", layout="wide")

st.title("नंबर स्प्रेडर व ग्रुप जनरेटर")

# इनपुट बॉक्स
raw_input = st.text_area("यहाँ अपने 90 नंबर कॉमा (,) लगाकर पेस्ट करें:", placeholder="00, 01, 02, 03...")

if st.button("जनरेट करें (Generate)", type="primary"):
    if not raw_input.strip():
        st.warning("कृपया नंबर दर्ज करें!")
    else:
        # नंबर अलग करें
        numbers = [num.strip() for num in raw_input.split(',') if num.strip()]
        
        # नंबरों को रैंडम मिक्स (Shuffle) करें
        random.shuffle(numbers)
        
        # 4 ग्रुप में बांटें
        group_a = numbers[0:20]
        group_b = numbers[20:40]
        group_c = numbers[40:65]
        group_d = numbers[65:90]
        
        groups = [
            {"name": "ग्रुप A (20 नंबर)", "data": group_a},
            {"name": "ग्रुप B (20 नंबर)", "data": group_b},
            {"name": "ग्रुप C (25 नंबर)", "data": group_c},
            {"name": "ग्रुप D (25 नंबर)", "data": group_d}
        ]
        
        cols = st.columns(4)
        
        for idx, grp in enumerate(groups):
            with cols[idx]:
                st.subheader(grp["name"])
                if grp["data"]:
                    # मुख्य ग्रुप
                    st.info(", ".join(grp["data"]))
                    
                    # सब-ग्रुप्स
                    sub1 = " / ".join(grp["data"][0:5]) + " (100)" if len(grp["data"]) >= 5 else ""
                    sub2 = " _ ".join(grp["data"][5:9]) + " (100)" if len(grp["data"]) >= 9 else ""
                    sub3 = " - ".join(grp["data"][9:13]) + " (100)" if len(grp["data"]) >= 13 else ""
                    sub4 = ", ".join(grp["data"][13:16]) + " (100)" if len(grp["data"]) >= 16 else ""
                    sub5 = " . ".join(grp["data"][16:]) + " (100)" if len(grp["data"]) > 16 else ""
                    
                    if sub1: st.write(f"**1.** {sub1}")
                    if sub2: st.write(f"**2.** {sub2}")
                    if sub3: st.write(f"**3.** {sub3}")
                    if sub4: st.write(f"**4.** {sub4}")
                    if sub5: st.write(f"**5.** {sub5}")
