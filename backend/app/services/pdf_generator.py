"""
ITR-1 SAHAJ PDF Generator
=========================
Generates official ITR-1 SAHAJ format PDF for Indian Income Tax Return.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from datetime import datetime
from typing import Dict, Any


def generate_itr1_pdf(data: Dict[str, Any]) -> bytes:
    """
    Generate ITR-1 SAHAJ format PDF from conversational filing data.
    
    Args:
        data: Extracted tax data from conversational filing
        
    Returns:
        PDF bytes
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'ITRTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=colors.HexColor('#1a365d')
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=11,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.HexColor('#2c5282'),
        backColor=colors.HexColor('#e2e8f0'),
        borderPadding=4
    )
    
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#4a5568')
    )
    
    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold'
    )
    
    # Extract data
    personal = data.get('personal_info', {})
    income = data.get('income', {})
    deductions = data.get('deductions', {})
    regime = data.get('regime', 'new')
    fy = data.get('financial_year', '2024-2025')
    
    # Calculate values
    salary = income.get('salary', 0) or 0
    other_income = income.get('other_income', 0) or 0
    total_income = salary + other_income
    
    d80c = min(deductions.get('section_80c', 0) or 0, 150000)
    d80d = min(deductions.get('section_80d', 0) or 0, 25000)
    total_deductions = d80c + d80d
    
    standard_deduction = 50000
    taxable_income = max(0, total_income - standard_deduction - (total_deductions if regime == 'old' else 0))
    
    # Calculate tax
    tax = calculate_tax(taxable_income, regime)
    rebate = calculate_rebate(taxable_income, tax, regime)
    tax_after_rebate = max(0, tax - rebate)
    cess = tax_after_rebate * 0.04
    total_tax = tax_after_rebate + cess
    
    # =========================================================================
    # HEADER
    # =========================================================================
    
    header_data = [
        ['INCOME TAX DEPARTMENT', ''],
        ['GOVERNMENT OF INDIA', ''],
        ['', ''],
        ['ITR-1 SAHAJ', f'Assessment Year: {fy}'],
    ]
    
    header_table = Table(header_data, colWidths=[350, 150])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 14),
        ('FONTSIZE', (0, 1), (0, 1), 12),
        ('FONTSIZE', (0, 3), (-1, 3), 12),
        ('TEXTCOLOR', (0, 0), (0, 1), colors.HexColor('#1a365d')),
        ('FONTNAME', (0, 3), (0, 3), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#e2e8f0')),
        ('BOX', (0, 3), (-1, 3), 1, colors.HexColor('#2c5282')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 12))
    
    # Tax Regime Badge
    regime_text = f"Tax Regime: {'NEW REGIME (Section 115BAC)' if regime == 'new' else 'OLD REGIME'}"
    regime_color = colors.HexColor('#48bb78') if regime == 'new' else colors.HexColor('#ed8936')
    story.append(Paragraph(f"<font color='{regime_color}'><b>{regime_text}</b></font>", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # =========================================================================
    # PART A: GENERAL INFORMATION
    # =========================================================================
    
    story.append(Paragraph("PART A - GENERAL INFORMATION", section_style))
    
    part_a_data = [
        ['PAN', personal.get('pan_number', 'Not Provided'), 'Assessment Year', fy],
        ['Name', personal.get('name', 'Not Provided'), 'Email', personal.get('email', 'Not Provided')],
        ['Status', 'Individual (Resident)', 'Filing Type', 'Original Return u/s 139(1)'],
    ]
    
    part_a_table = Table(part_a_data, colWidths=[80, 170, 80, 170])
    part_a_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f7fafc')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f7fafc')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(part_a_table)
    story.append(Spacer(1, 16))
    
    # =========================================================================
    # PART B: GROSS TOTAL INCOME
    # =========================================================================
    
    story.append(Paragraph("PART B - GROSS TOTAL INCOME", section_style))
    
    part_b_data = [
        ['', 'Description', 'Amount (₹)'],
        ['B1', 'Income from Salary/Pension', ''],
        ['', f'   Employer: {income.get("employer_name", "N/A")}', ''],
        ['', '   Gross Salary u/s 17(1)', format_currency(salary)],
        ['', '   Less: Standard Deduction u/s 16(ia)', f'(-) {format_currency(standard_deduction)}'],
        ['', '   Net Salary Income', format_currency(max(0, salary - standard_deduction))],
        ['B2', 'Income from House Property', format_currency(0)],
        ['B3', 'Income from Other Sources', format_currency(other_income)],
        ['B4', 'Gross Total Income (B1+B2+B3)', format_currency(total_income - standard_deduction)],
    ]
    
    part_b_table = Table(part_b_data, colWidths=[30, 300, 170])
    part_b_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f7fafc')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e2e8f0')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(part_b_table)
    story.append(Spacer(1, 16))
    
    # =========================================================================
    # PART C: DEDUCTIONS (Chapter VI-A)
    # =========================================================================
    
    story.append(Paragraph("PART C - DEDUCTIONS UNDER CHAPTER VI-A", section_style))
    
    if regime == 'old':
        part_c_data = [
            ['Section', 'Description', 'Claimed (₹)', 'Max Limit'],
            ['80C', 'PPF, ELSS, LIC, etc.', format_currency(d80c), '₹1,50,000'],
            ['80D', 'Health Insurance Premium', format_currency(d80d), '₹25,000'],
            ['80CCD(1B)', 'NPS Additional', format_currency(0), '₹50,000'],
            ['80TTA', 'Savings Interest', format_currency(0), '₹10,000'],
            ['', 'Total Deductions', format_currency(total_deductions), ''],
        ]
    else:
        part_c_data = [
            ['Section', 'Description', 'Claimed (₹)', 'Status'],
            ['', 'Under New Regime, most deductions are NOT available', '', ''],
            ['80CCD(2)', 'Employer NPS Contribution', format_currency(0), 'Allowed'],
            ['', 'Total Deductions', format_currency(0), ''],
        ]
    
    part_c_table = Table(part_c_data, colWidths=[70, 230, 100, 100])
    part_c_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e2e8f0')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(part_c_table)
    story.append(Spacer(1, 16))
    
    # =========================================================================
    # PART D: TAX COMPUTATION
    # =========================================================================
    
    story.append(Paragraph("PART D - COMPUTATION OF TAX PAYABLE", section_style))
    
    part_d_data = [
        ['', 'Particulars', 'Amount (₹)'],
        ['D1', 'Gross Total Income', format_currency(total_income - standard_deduction)],
        ['D2', 'Less: Deductions under Chapter VI-A', f'(-) {format_currency(total_deductions if regime == "old" else 0)}'],
        ['D3', 'Total Taxable Income (D1-D2)', format_currency(taxable_income)],
        ['D4', 'Tax on Total Income', format_currency(tax)],
        ['D5', 'Less: Rebate u/s 87A', f'(-) {format_currency(rebate)}'],
        ['D6', 'Tax after Rebate', format_currency(tax_after_rebate)],
        ['D7', 'Add: Health & Education Cess (4%)', format_currency(cess)],
        ['D8', 'Total Tax Payable', format_currency(total_tax)],
    ]
    
    part_d_table = Table(part_d_data, colWidths=[30, 300, 170])
    part_d_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#48bb78')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(part_d_table)
    story.append(Spacer(1, 20))
    
    # =========================================================================
    # TAX SLABS REFERENCE
    # =========================================================================
    
    story.append(Paragraph("TAX SLABS APPLIED", section_style))
    
    if regime == 'new':
        slabs_data = [
            ['Income Range', 'Tax Rate'],
            ['₹0 - ₹3,00,000', 'Nil'],
            ['₹3,00,001 - ₹6,00,000', '5%'],
            ['₹6,00,001 - ₹9,00,000', '10%'],
            ['₹9,00,001 - ₹12,00,000', '15%'],
            ['₹12,00,001 - ₹15,00,000', '20%'],
            ['Above ₹15,00,000', '30%'],
        ]
    else:
        slabs_data = [
            ['Income Range', 'Tax Rate'],
            ['₹0 - ₹2,50,000', 'Nil'],
            ['₹2,50,001 - ₹5,00,000', '5%'],
            ['₹5,00,001 - ₹10,00,000', '20%'],
            ['Above ₹10,00,000', '30%'],
        ]
    
    slabs_table = Table(slabs_data, colWidths=[250, 100])
    slabs_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(slabs_table)
    story.append(Spacer(1, 20))
    
    # =========================================================================
    # FOOTER / VERIFICATION
    # =========================================================================
    
    story.append(Paragraph("VERIFICATION", section_style))
    
    verification_text = f"""
    I, <b>{personal.get('name', 'THE ASSESSEE')}</b>, do hereby declare that what is stated above is true 
    to the best of my knowledge and belief, that the return is correct and complete, 
    and that I am filing this return in my capacity as <b>SELF</b>.
    """
    story.append(Paragraph(verification_text, styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Signature area
    sig_data = [
        ['Place:', '_____________', 'Signature:', '_____________'],
        ['Date:', datetime.now().strftime('%d-%m-%Y'), '', ''],
    ]
    sig_table = Table(sig_data, colWidths=[50, 150, 80, 200])
    story.append(sig_table)
    
    story.append(Spacer(1, 30))
    
    # Disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer', 
        parent=styles['Normal'], 
        fontSize=7, 
        textColor=colors.HexColor('#718096'),
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        "This is a computer-generated ITR-1 SAHAJ summary prepared by TaxFluent AI. "
        "For official filing, please submit through the Income Tax e-Filing Portal (incometax.gov.in). "
        f"Generated on {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}.",
        disclaimer_style
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def format_currency(amount: float) -> str:
    """Format amount in Indian currency style."""
    if amount == 0:
        return "₹0"
    
    amount = abs(amount)
    
    # Indian numbering system (lakhs, crores)
    if amount >= 10000000:
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:
        return f"₹{amount/100000:.2f} L"
    else:
        # Format with commas in Indian style
        s = f"{amount:,.0f}"
        return f"₹{s}"


def calculate_tax(taxable_income: float, regime: str) -> float:
    """Calculate tax based on regime."""
    if regime == 'new':
        # New Regime (Section 115BAC) - FY 2023-24
        slabs = [
            (300000, 0),
            (600000, 0.05),
            (900000, 0.10),
            (1200000, 0.15),
            (1500000, 0.20),
            (float('inf'), 0.30),
        ]
    else:
        # Old Regime
        slabs = [
            (250000, 0),
            (500000, 0.05),
            (1000000, 0.20),
            (float('inf'), 0.30),
        ]
    
    tax = 0
    prev = 0
    for limit, rate in slabs:
        if taxable_income <= prev:
            break
        taxable_in_slab = min(taxable_income, limit) - prev
        tax += taxable_in_slab * rate
        prev = limit
    
    return tax


def calculate_rebate(taxable_income: float, tax: float, regime: str) -> float:
    """Calculate rebate under Section 87A."""
    if regime == 'new' and taxable_income <= 700000:
        return min(tax, 25000)
    elif regime == 'old' and taxable_income <= 500000:
        return min(tax, 12500)
    return 0


# Keep the old function for backward compatibility
def generate_tax_return_pdf(user_data: dict, tax_data: dict) -> bytes:
    """Legacy function - converts to new format."""
    # Convert old format to new format
    data = {
        "personal_info": {
            "name": f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            "pan_number": user_data.get('pan', ''),
            "email": user_data.get('email', ''),
        },
        "income": {
            "employer_name": tax_data.get('w2s', [{}])[0].get('employer', 'Unknown') if tax_data.get('w2s') else 'Unknown',
            "salary": sum(w.get('wages', 0) for w in tax_data.get('w2s', [])),
            "other_income": sum(f.get('amount', 0) for f in tax_data.get('form1099s', [])),
        },
        "deductions": {},
        "regime": "new",
        "financial_year": f"{datetime.now().year-1}-{datetime.now().year}",
    }
    
    return generate_itr1_pdf(data)
