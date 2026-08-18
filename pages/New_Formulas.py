# ================= FORMULA 5 (3-4 DAYS MULTI-GAME CONTINUOUS PATTERN ENGINE) =================
    st.subheader("5️⃣ Multi-Day & Multi-Game Arithmetic Sequence Predictor")
    
    # कम से कम 4 दिनों का डेटा होना चाहिए
    if len(df) >= 4:
        num_days = st.slider("इतिहास के कितने दिनों का सीक्वेंस देखना है?", 3, 5, 4, key="f5_days_slider")
        
        # पिछले n दिनों का डेटा
        sub_df = df.tail(num_days).reset_index(drop=True)
        
        st.write(f"📌 **पिछले {num_days} दिनों का 6-गेम डेटा बोर्ड:**")
        st.dataframe(sub_df[['Date'] + available_cols] if 'Date' in sub_df.columns else sub_df[available_cols], use_container_width=True)
        
        detected_patterns = []
        
        # सभी गेम के जोड़ों (Pairs) की आपस में तुलना (जैसे GALI -> DB, SG -> GZBD आदि)
        for source_g in available_cols:
            for target_g in available_cols:
                if source_g == target_g:
                    continue
                
                # पिछले दिनों के डिफ़्रेंस निकालना
                diff_history = []
                for d in range(num_days - 1):
                    val_src = sub_df.loc[d, source_g]
                    val_tgt = sub_df.loc[d + 1, target_g]
                    
                    if pd.notna(val_src) and pd.notna(val_tgt):
                        # 0-99 की रेंज में मोड्यूलो अंतर
                        diff = (int(val_tgt) - int(val_src)) % 100
                        diff_history.append(diff)
                
                # यदि पर्याप्त दिनों का डिफ़्रेंस मिल जाए
                if len(diff_history) >= (num_days - 1):
                    # 1. जाँचें कि क्या डिफ़्रेंस में एक निश्चित बढ़त/घटत का सीक्वेंस है (उदा: -7, -6, -5...)
                    step_changes = [diff_history[i+1] - diff_history[i] for i in range(len(diff_history)-1)]
                    
                    # अगर लगातार एक समान स्टेप से अंतर बदल रहा हो
                    if len(set(step_changes)) == 1:
                        step = step_changes[0]
                        next_expected_diff = (diff_history[-1] + step) % 100
                        
                        last_src_val = sub_df.loc[num_days - 1, source_g]
                        if pd.notna(last_src_val):
                            pred_num = (int(last_src_val) + next_expected_diff) % 100
                            
                            detected_patterns.append({
                                "पैटर्न का प्रकार": "लगातार घटता/बढ़ता क्रम (Step Sequence)",
                                "गेम कनेक्शन": f"{source_g} ➔ {target_g}",
                                "पिछले {}-दिनों का डिफ़्रेंस".format(num_days-1): " ➔ ".join([f"{d:+}" for d in diff_history]),
                                "आज का संभावित अंतर (Expected Diff)": f"{next_expected_diff:+}",
                                "आज आने वाला नंबर": f"{pred_num:02d}",
                                "फैमिली": str(get_family(pred_num))
                            })
                    
                    # 2. जाँचें कि क्या पिछले 3-4 दिनों से बिल्कुल सेम डिफ़्रेंस रिपीट हो रहा है (उदा: -5, -5, -5...)
                    elif len(set(diff_history)) == 1:
                        same_diff = diff_history[0]
                        last_src_val = sub_df.loc[num_days - 1, source_g]
                        if pd.notna(last_src_val):
                            pred_num = (int(last_src_val) + same_diff) % 100
                            
                            detected_patterns.append({
                                "पैटर्न का प्रकार": "समान अंतर रिपीट (Fixed Repeat Diff)",
                                "गेम कनेक्शन": f"{source_g} ➔ {target_g}",
                                "पिछले {}-दिनों का डिफ़्रेंस".format(num_days-1): " ➔ ".join([f"{d:+}" for d in diff_history]),
                                "आज का संभावित अंतर (Expected Diff)": f"{same_diff:+}",
                                "आज आने वाला नंबर": f"{pred_num:02d}",
                                "फैमिली": str(get_family(pred_num))
                            })

        if detected_patterns:
            st.success(f"🔥 **कुल `{len(detected_patterns)}` लगातार 3-4 दिनों के क्रॉस-गेम पैटर्न मिले हैं!**")
            st.table(pd.DataFrame(detected_patterns))
        else:
            st.warning("⚠️ पिछले 3-4 दिनों में कोई लगातार घटता/बढ़ता या सेम डिफ़्रेंस वाला पैटर्न नहीं मिला।")
    else:
        st.error("डेटाबेस में कम से कम 4 दिनों का डेटा होना आवश्यक है।")
