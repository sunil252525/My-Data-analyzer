import pandas as pd
import re
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Hisab & Calculation Dashboard", page_icon="💰", layout="wide"
)

st.title("💰 Daily Hisab & Calculation Sheet")
st.markdown("---")

# Categories matching your sheet layout
CATEGORIES = [
    "Delhi Bazar",
    "Shri Ganesh",
    "Faridabad",
    "Gaziyabad",
    "Gali",
    "Ds",
]

# Initialize Session State
if "entry_data" not in st.session_state:
    st.session_state.entry_data = {cat: [] for cat in CATEGORIES}


def parse_input_string(text):
    """Parse text formatted like '0, 1, 6, 7, 8, 9(100)' or '23, 27, 12(50)'

    Extracts numbers, counts them, extracts rate from parentheses, and calculates amount.
    """
    text = str(text).strip()
    if not text:
        return 0, 0, 0.0

    match = re.search(r"\((.*?)\)", text)
    rate = 0.0
    if match:
        try:
            rate = float(match.group(1))
        except ValueError:
            rate = 0.0
        # Remove parenthesized rate to get numbers list
        numbers_part = text[: match.start()].strip()
    else:
        numbers_part = text

    # Split numbers by comma or space
    raw_nums = [
        n.strip() for n in re.split(r"[,,\s]+", numbers_part) if n.strip()
    ]
    total_nums = len(raw_nums)
    total_amount = total_nums * rate

    return total_nums, rate, total_amount


# Sidebar Controls
st.sidebar.header("⚙️ Settings & Controls")
passing_multiplier = st.sidebar.number_input(
    "Passing Multiplier (पासिंग गुना)", min_value=1.0, value=90.0, step=1.0
)

# Tabs for inputs and summary
tab_input, tab_summary = st.tabs(
    ["📝 Entry & Calculation", "📊 Summary & Export"]
)

with tab_input:
    st.subheader("Enter Records by Category")
    cols = st.columns(len(CATEGORIES))

    all_totals = {}

    for idx, category in enumerate(CATEGORIES):
        with cols[idx]:
            st.markdown(f"### {category}")

            # Text input area for quick paste or entry
            raw_input = st.text_area(
                f"Enter Raw Lines for {category}",
                placeholder="e.g.\n0, 1, 6, 7(100)\n23, 27, 12(50)",
                key=f"raw_{category}",
                height=120,
            )

            # Button to parse lines automatically
            if st.button(f"Add Lines", key=f"btn_{category}"):
                lines = raw_input.strip().split("\n")
                for line in lines:
                    if line.strip():
                        n_count, r_val, amt = parse_input_string(line)
                        st.session_state.entry_data[category].append(
                            {
                                "Input (A)": line.strip(),
                                "Total Numbers": n_count,
                                "Rate": r_val,
                                "Total Amount": amt,
                                "Passing Into": 0.0,
                                "Total Return": 0.0,
                            }
                        )
                st.rerun()

            # Display table with editable details
            if st.session_state.entry_data[category]:
                df_cat = pd.DataFrame(st.session_state.entry_data[category])

                # Recalculate Totals & Returns
                df_cat["Total Amount"] = (
                    df_cat["Total Numbers"] * df_cat["Rate"]
                )
                df_cat["Total Return"] = (
                    df_cat["Passing Into"] * df_cat["Rate"] * passing_multiplier
                )

                st.session_state.entry_data[category] = df_cat.to_dict(
                    "records"
                )

                cat_total_amt = df_cat["Total Amount"].sum()
                cat_total_return = df_cat["Total Return"].sum()
                net_balance = cat_total_amt - cat_total_return

                st.markdown(f"**Total Amount:** ₹{cat_total_amt:,.2f}")
                st.markdown(f"**Total Return:** ₹{cat_total_return:,.2f}")
                st.markdown(f"**Net:** ₹{net_balance:,.2f}")

                if st.button(f"Clear {category}", key=f"clear_{category}"):
                    st.session_state.entry_data[category] = []
                    st.rerun()
            else:
                st.info("No entries yet.")

with tab_summary:
    st.subheader(" Overall Summary")

    summary_rows = []
    grand_amount = 0.0
    grand_return = 0.0

    for cat in CATEGORIES:
        entries = st.session_state.entry_data[cat]
        if entries:
            df_temp = pd.DataFrame(entries)
            tot_amt = df_temp["Total Amount"].sum()
            tot_ret = df_temp["Total Return"].sum()
            summary_rows.append(
                {
                    "Category": cat,
                    "Total Entries": len(entries),
                    "Total Amount (₹)": tot_amt,
                    "Total Return (₹)": tot_ret,
                    "Net Amount (₹)": tot_amt - tot_ret,
                }
            )
            grand_amount += tot_amt
            grand_return += tot_ret

    if summary_rows:
        df_summary = pd.DataFrame(summary_rows)
        st.dataframe(df_summary, use_container_width=True)

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Grand Total Amount", f"₹{grand_amount:,.2f}")
        col_m2.metric("Grand Total Return", f"₹{grand_return:,.2f}")
        col_m3.metric(
            "Final Net Balance",
            f"₹{grand_amount - grand_return:,.2f}",
            delta_color="normal",
        )

        # Export CSV Button
        csv_data = pd.DataFrame()
        for cat in CATEGORIES:
            if st.session_state.entry_data[cat]:
                df_temp = pd.DataFrame(st.session_state.entry_data[cat])
                df_temp["Category"] = cat
                csv_data = pd.concat([csv_data, df_temp], ignore_index=True)

        if not csv_data.empty:
            st.download_button(
                label="📥 Download Hisab CSV Report",
                data=csv_data.to_csv(index=False),
                file_name="Daily_Hisab_Report.csv",
                mime="text/csv",
            )
    else:
        st.info("No data available to build summary.")
