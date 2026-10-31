import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

st.set_page_config(page_title="Property PDF Generator", page_icon="📄", layout="centered")

st.title("🏡 Property Details PDF Generator")
st.write("अपनी प्रॉपर्टी की जानकारी भरें और एक क्लिक में प्रोफेशनल पीडीएफ डाउनलोड करें।")

with st.form("property_form"):
    st.subheader("प्रॉपर्टी की मुख्य जानकारी")
    
    project_name = st.text_input("प्रोजेक्ट / प्रॉपर्टी का नाम", "Prime Expressway Corridor Land")
    property_type = st.text_input("प्रॉपर्टी का प्रकार", "AGRICULTURE / INVESTMENT")
    location = st.text_input("प्रॉपर्टी लोकेशन / कोऑर्डिनेट्स", "Mohna Area, Faridabad (28.230928, 77.436950)")
    total_area = st.text_input("कुल क्षेत्रफल (Total Plot Area)", "9.5 ACRE")
    owner_name = st.text_input("मालिक / कंपनी का नाम", "A Star Mega Developer & Land Corp")
    farming_details = st.text_input("पेड़ / फसल या खास बातें", "Fertile agricultural land patch")
    road_infra = st.text_input("रास्ता / इंफ्रास्ट्रक्चर", "1 Side Open, Wide Road Access")
    landmark = st.text_input("लैंडमार्क (आसपास की मुख्य जगह)", "Near KMP Expressway Interchange")
    price = st.text_input("मांगी गई कीमत (Price)", "₹ 6.5 Crore Per Acre")
    
    submitted = st.form_submit_button("Generate PDF")

if submitted:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1A365D'),
        alignment=1,
        spaceAfter=15
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=10,
        spaceAfter=6
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=4
    )
    
    story = []
    story.append(Paragraph("EXCLUSIVE PROPERTY BRIEFING", title_style))
    story.append(Paragraph("-" * 50, title_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("📋 Project Overview", heading_style))
    story.append(Paragraph(f"<b>Project Name:</b> {project_name}", normal_style))
    story.append(Paragraph(f"<b>Property Type:</b> {property_type}", normal_style))
    story.append(Paragraph(f"<b>Location / Coordinates:</b> {location}", normal_style))
    story.append(Paragraph(f"<b>Total Area:</b> {total_area}", normal_style))
    story.append(Paragraph(f"<b>Owner / Company:</b> {owner_name}", normal_style))
    
    story.append(Paragraph("📍 Infrastructure & Connectivity", heading_style))
    story.append(Paragraph(f"<b>Road Infrastructure:</b> {road_infra}", normal_style))
    story.append(Paragraph(f"<b>Key Landmark:</b> {landmark}", normal_style))
    story.append(Paragraph(f"<b>Features / Farming:</b> {farming_details}", normal_style))
    
    story.append(Paragraph("💰 Commercial Details", heading_style))
    story.append(Paragraph(f"<b>Required Amount / Price:</b> {price}", normal_style))
    
    doc.build(story)
    buffer.seek(0)
    
    st.success("पीडीएफ सफलतापूर्वक तैयार हो गई है!")
    st.download_button(
        label="📥 Download PDF Now",
        data=buffer,
        file_name="property_details.pdf",
        mime="application/pdf"
    )
