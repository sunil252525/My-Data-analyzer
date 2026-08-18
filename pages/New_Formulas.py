# ================= FORMULA 5 (ALL 6 GAMES CONTINUOUS CROSS-CHAIN ENGINE) =================
    st.subheader("5️⃣ All 6-Games Continuous Plus/Minus & Step Predictor Engine")
    
    # 1. 6 की 6 गेम के सबसे हालिया परिणामों की एक सीधी लड़ी (Chain) बनाना
    latest_row = df.iloc[-1]  # आज/हालिया रो
    prev_row = df.iloc[-2] if len(df) > 1 else None  # पिछली रो
    
    chain_results = []
    # यदि आज की रो अधूरी है तो पिछली रो और आज की रो को मिलाकर लगातार लड़ी बनाते हैं
    if prev_row is not None:
        for c in available_cols:
            if pd.notna(prev_row[c]): chain_results.append((c, int(prev_row[c])))
    for c in available_cols:
        if pd.notna(latest_row[c]): chain_results.append((c, int(latest_row[c])))
    
    # लड़ी के पिछले 6 सबसे हालिया गेम के रिजल्ट्स
    recent_chain = chain_results[-6:] if len(chain_results) >= 6 else chain_results
    
    chain_vals = [val for game, val in recent_chain]
    chain_names = [game for game, val in recent_chain]

    st.info(f"📌 **लगातार 6 गेमों की हालिया लड़ी (Chain):** " + " ➔ ".join([f"{g}: `{v:02d}`" for g, v in recent_chain]))

    if len(chain_vals) >= 3:
        # हालिया गेमों के बीच का प्लस/माइनस अंतर
        diffs = [(chain_vals[i+1] - chain_vals[i]) % 100 for i in range(len(chain_vals)-1)]
        
        last_game_name, last_val = recent_chain[-1]
        
        st.write(f"📈 **गेम-टू-गेम आपस में अंतर (Cross-Game Differences):** " + " ➔ ".join([f"({d:+})" for d in diffs]))

        # संभावित पैटर्न की गणना (आज आने वाले अगले नंबर हेतु)
        predictions = []

        # 1. यदि लगातार समान डिफ़्रेंस चल रहा हो (+1, +1, +1 या +2, +2, +2 आदि)
        last_diff = diffs[-1]
        same_step_num = (last_val + last_diff) % 100
        predictions.append({
            "पैटर्न का प्रकार (Pattern Step)": f"समान अंतर पैटर्न (Same Diff {last_diff:+})",
            "कैलकुलेशन (Logic)": f"पिछला रिजल्ट ({last_val:02d}) {last_diff:+} ",
            "आज आने वाला अगला संभावित नंबर": f"{same_step_num:02d}",
            "फैमिली": str(get_family(same_step_num))
        })

        # 2. यदि 1 का प्रोग्रेशन चल रहा हो (+1 या -1 का सीधा कदम)
        plus1_num = (last_val + 1) % 100
        predictions.append({
            "पैटर्न का प्रकार (Pattern Step)": "+1 सीधा कदम (+1 Step)",
            "कैलकुलेशन (Logic)": f"पिछला रिजल्ट ({last_val:02d}) + 1",
            "आज आने वाला अगला संभावित नंबर": f"{plus1_num:02d}",
            "फैमिली": str(get_family(plus1_num))
        })

        minus1_num = (last_val - 1) % 100
        predictions.append({
            "पैटर्न का प्रकार (Pattern Step)": "-1 सीधा कदम (-1 Step)",
            "कैलकुलेशन (Logic)": f"पिछला रिजल्ट ({last_val:02d}) - 1",
            "आज आने वाला अगला संभावित नंबर": f"{minus1_num:02d}",
            "फैमिली": str(get_family(minus1_num))
        })

        # 3. यदि अंतर 1-1 बढ़ता या घटता जा रहा हो (+1, +2 -> Next +3)
        if len(diffs) >= 2:
            diff_change = diffs[-1] - diffs[-2]
            next_diff = (diffs[-1] + diff_change) % 100
            prog_num = (last_val + next_diff) % 100
            predictions.append({
                "पैटर्न का प्रकार (Pattern Step)": f"अंतर बढ़ता/घटता क्रम (Progression Diff {next_diff:+})",
                "कैलकुलेशन (Logic)": f"पिछला रिजल्ट ({last_val:02d}) {next_diff:+}",
                "आज आने वाला अगला संभावित नंबर": f"{prog_num:02d}",
                "फैमिली": str(get_family(prog_num))
            })

        st.success(f"🎯 **`{last_game_name}` ({last_val:02d}) के बाद आने वाली अगली गेम के संभावित गणितीय नंबर:**")
        st.table(pd.DataFrame(predictions))
