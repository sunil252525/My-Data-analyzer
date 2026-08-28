import openpyxl
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment

# 1. आपकी मुख्य एक्सेल फ़ाइल को लोड करना[span_1](start_span)[span_1](end_span)
source_file = "Colour combination file.xlsx"
wb = openpyxl.load_workbook(source_file, data_only=True)

report_data = []

# 2. पिछले सालों के समान महीने का पैटर्न स्कैन करना (Sheet9)[span_2](start_span)[span_2](end_span)
if 'Sheet9' in wb.sheetnames:
    ws = wb['Sheet9']
    for r in range(4, 35): # 1 से 31 तारीख तक की चेकिंग[span_3](start_span)[span_3](end_span)
        tariq = ws.cell(row=r, column=7).value
        if not tariq:
            continue
        
        # 2026, 2025, और 2024 के नंबर निकालना[span_4](start_span)[span_4](end_span)
        v26 = [str(ws.cell(row=r, column=c).value).strip() for c in [8, 9, 11, 12, 13, 14] if ws.cell(row=r, column=c).value and str(ws.cell(row=r, column=c).value).strip() != 'XX']
        v25 = [str(ws.cell(row=r, column=c).value).strip() for c in [18, 19, 21, 22, 23, 24] if ws.cell(row=r, column=c).value and str(ws.cell(row=r, column=c).value).strip() != 'XX']
        v24 = [str(ws.cell(row=r, column=c).value).strip() for c in [27, 28, 30, 31, 32, 33] if ws.cell(row=r, column=c).value and str(ws.cell(row=r, column=c).value).strip() != 'XX']
        
        # रिपीट/मैचिंग नंबर खोजना[span_5](start_span)[span_5](end_span)
        match_25 = set(v26).intersection(set(v25))
        match_24 = set(v26).intersection(set(v24))
        
        report_data.append({
            "तारीख (Date)": f"तारीख {tariq}",
            "जून 2026": ", ".join(v26),
            "जून 2025": ", ".join(v25),
            "2026 vs 2025 रिपीट": ", ".join(match_25) if match_25 else "None",
            "2026 vs 2024 रिपीट": ", ".join(match_24) if match_24 else "None"
        })

# 3. नया एक्सेल रिपोर्ट तैयार करना[span_6](start_span)[span_6](end_span)
df = pd.DataFrame(report_data)
out_wb = openpyxl.Workbook()
ws_out = out_wb.active
ws_out.title = "Pattern Report"

ws_out.append(list(df.columns))
for row in df.values:
    ws_out.append(list(row))

# 4. रिपोर्ट सेव करना[span_7](start_span)[span_7](end_span)
out_wb.save("Pattern_Analysis_Report.xlsx")
print("एनालिसिस पूरा हो गया है! 'Pattern_Analysis_Report.xlsx' नाम से नई फ़ाइल बन गई है।")
