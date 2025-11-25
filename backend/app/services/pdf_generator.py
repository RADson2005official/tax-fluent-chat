from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from datetime import datetime

def generate_tax_return_pdf(user_data: dict, tax_data: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = styles['Heading1']
    story.append(Paragraph(f"Tax Return Summary - {datetime.now().year}", title_style))
    story.append(Spacer(1, 12))

    # User Info
    story.append(Paragraph("Taxpayer Information", styles['Heading2']))
    user_info = [
        ["Name", f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}"],
        ["Email", user_data.get('email', '')],
        ["Filing Status", tax_data.get('filing_status', 'Single')]
    ]
    t = Table(user_info, colWidths=[150, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Income Summary
    story.append(Paragraph("Income Summary", styles['Heading2']))
    income_data = [["Source", "Amount"]]
    total_income = 0
    
    # W-2s
    for w2 in tax_data.get('w2s', []):
        amount = float(w2.get('wages', 0))
        income_data.append([f"W-2: {w2.get('employer', 'Unknown')}", f"${amount:,.2f}"])
        total_income += amount
        
    # 1099s
    for form1099 in tax_data.get('form1099s', []):
        amount = float(form1099.get('amount', 0))
        income_data.append([f"1099: {form1099.get('payer', 'Unknown')}", f"${amount:,.2f}"])
        total_income += amount

    income_data.append(["Total Income", f"${total_income:,.2f}"])

    t_income = Table(income_data, colWidths=[300, 150])
    t_income.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t_income)
    story.append(Spacer(1, 12))

    # Tax Calculation (Mock)
    story.append(Paragraph("Tax Calculation", styles['Heading2']))
    tax_rate = 0.20  # Flat 20% for simplicity
    tax_due = total_income * tax_rate
    
    calc_data = [
        ["Total Income", f"${total_income:,.2f}"],
        ["Tax Rate", "20%"],
        ["Estimated Tax Due", f"${tax_due:,.2f}"]
    ]
    
    t_calc = Table(calc_data, colWidths=[300, 150])
    t_calc.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, -1), (-1, -1), colors.yellow)
    ]))
    story.append(t_calc)
    
    # Disclaimer
    story.append(Spacer(1, 24))
    disclaimer_style = ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
    story.append(Paragraph("This is a generated summary for demonstration purposes only. Not a legal tax document.", disclaimer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
