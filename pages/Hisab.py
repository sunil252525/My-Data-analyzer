import re
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Advance Hisab Calculator", page_icon="💰", layout="wide"
)

st.title("💰 Advance Hisab & Daily Ledger Calculator")
st.markdown("---")

# Categories
CATEGORIES = [
    "Delhi Bazar",
    "Shri Ganesh",
    "Faridabad",
    "Gaziyabad",
    "Gali",
    "Ds",
]

if "entry_data" not in st.session_state:
    st.session_state.entry_data = {cat: [] for cat in CATEGORIES}


def parse_line(line):
    """सही से नंबर्स, क्रॉसिंग, हरुफ़ और रेट निकालने का फंक्शन"""
    line = line.strip()
    if not line:
        return 0, 0.0, 0.0

    # 1. ब्रैकेट () से रेट निकालें
    rate_match = re.search(r"\((.*?)\)", line)
    rate = 0.0
    if rate_match:
        try:
            rate = float(rate_match.group(1))
        except ValueError:
            rate = 0.0
        content = line[: rate_match.start()].strip()
    else:
        # अगर ब्रैकेट नहीं है तो आख़िरी संख्या को रेट मान सकते हैं या 0
        content = line

    # 2. अगर "cross" शब्द लिखा है (जैसे 1234 cross)
    if "cross" in content.lower():
        digits = re.findall(r"\d", content)
        # N digits crossing = N * N numbers
        total_nums = len(digits) * len(digits)
    else:
        # साधारण नंबर्स की गिनती (Comma, space या dash से अलग किए गए)
        raw_nums = [
            n.strip() for n in re.split(r"[,,\s/-]+", content) if n.strip()
        ]
        total_nums = len(raw_nums)

    total_amount = total_nums * rate
    return total_nums, rate, total_amount


# Sidebar Settings
st.sidebar.header("⚙️ पासिंग सेटिंग्स")
pass_rate = st.sidebar.number_input(
    "पासिंग रेट (Passing Multiplier)", min_value=1.0, value=90.0, step=1.0
)

tab_entry, tab_report = st.tabs(
    ["📝 एंट्री और कैलकुलेशन", "📊 रिपोर्ट और समरी"]
)

with tab_entry:
    cols = st.columns(len(CATEGORIES))

    for idx, cat in enumerate(CATEGORIES):
        with cols[idx]:
            st.markdown(f"### {cat}")

            # Multiline Textbox
            input_text = st.text_area(
                f"एंट्री डालें ({cat})",
                placeholder="उदा:\n0, 1, 6, 7, 8, 9(100)\n23, 27, 12(50)",
                key=f"text_{cat}",
                height=150,
            )

            if st.button(f"जोड़ें ({cat})", key=f"add_{cat}"):
                lines = input_text.strip().split("\n")
                for l in lines:
                    if l.strip():
                        n_count, r_val, amt = parse_line(l)
                        st.session_state.entry_data[cat].append(
                            {
                                "Input Line": l.strip(),
                                "Total Numbers": n_count,
                                "Rate": r_val,
                                "Total Amount": amt,
                                "Passing Into": 0.0,
                            }
                        )
                st.rerun()

            # Display Data Table for Category
            if st.session_state.entry_data[cat]:
                df = pd.DataFrame(st.session_state.entry_data[cat])

                # Interactive table for Passing Into
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "Input Line": st.column_config.TextColumn("एंट्री"),
                        "Total Numbers": st.column_config.NumberColumn(
                            "कुल नंबर", disabled=True
                        ),
                        "Rate": st.column_config.NumberColumn(
                            "रेट", disabled=True
                        ),
                        "Total Amount": st.column_config.NumberColumn(
                            "कुल रकम (₹)", disabled=True
                        ),
                        "Passing Into": st.column_config.NumberColumn(
                            "पासिंग इनटू", min_value=0.0, step=10.0
                        ),
                    },
                    hide_index=True,
                    key=f"editor_{cat}",
                )

                # Update session state with edited passing
                st.session_state.entry_data[cat] = edited_df.to_dict("records")

                tot_amt = edited_df["Total Amount"].sum()
                tot_pass_into = edited_df["Passing Into"].sum()
                tot_return = tot_pass_into * pass_rate
                net = tot_return - tot_amt

                st.markdown(f"**कुल लगा पैसा:** ₹{tot_amt:,.0f}")
                st.markdown(f"**कुल वापसी (Pass):** ₹{tot_return:,.0f}")
                st.markdown(
                    f"**नेट (मुनाफा/घाटा):** {'+₹' if net>=0 else '-₹'}{abs(net):,.0f}"
                )

                if st.button("क्लियर करें", key=f"clear_{cat}"):
                    st.session_state.entry_data[cat] = []
                    st.rerun()

with tab_report:
    st.subheader("📋 ओवरऑल समरी (सभी गेम)")

    summary_data = []
    g_amt = 0.0
    g_pass_into = 0.0

    for cat in CATEGORIES:
        data = st.session_state.entry_data[cat]
        if data:
            df_c = pd.DataFrame(data)
            amt = df_c["Total Amount"].sum()
            p_into = df_c["Passing Into"].sum()
            ret = p_into * pass_rate

            g_amt += amt
            g_pass_into += p_into

            summary_data.append(
                {
                    "गेम (Category)": cat,
                    "कुल एंट्री": len(data),
                    "कुल लगा पैसा (₹)": amt,
                    "पासिंग इनटू": p_into,
                    "कुल वापसी (₹)": ret,
                    "नेट बैलेंस (₹)": ret - amt,
                }
            )

    if summary_data:
        sum_df = pd.DataFrame(summary_data)
        st.dataframe(sum_df, use_container_width=True)

        g_return = g_pass_into * pass_rate
        g_net = g_return - g_amt

        c1, c2, c3 = st.columns(3)
        c1.metric("कुल लगा पैसा", f"₹{g_amt:,.0f}")
        c2.metric("कुल वापसी (Payout)", f"₹{g_return:,.0f}")
        c3.metric(
            "फाइनल नेट हिसाब",
            f"₹{g_net:,.0f}",
            delta=f"{'मुनाफा' if g_net >= 0 else 'घाटा'}",
        )
    else:
        st.info("अभी कोई एंट्री नहीं की गई है।")
                
