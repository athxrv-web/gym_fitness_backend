"""
Payment Utilities - PDF Generation
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from django.core.files.base import ContentFile
from io import BytesIO


def generate_receipt_pdf(receipt):
    """Generate PDF receipt"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Title
    elements.append(Paragraph("PAYMENT RECEIPT", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Gym details
    gym = receipt.gym
    gym_info = [
        [Paragraph(f"<b>{gym.name}</b>", styles['Normal'])],
        [gym.address],
        [f"{gym.city}, {gym.state} - {gym.pincode}"],
        [f"Phone: {gym.phone}"],
        [f"Email: {gym.email}"],
    ]
    
    gym_table = Table(gym_info, colWidths=[6*inch])
    gym_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(gym_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Receipt details
    receipt_info = [
        ['Receipt Number:', receipt.receipt_number],
        ['Date:', receipt.created_at.strftime('%d-%b-%Y')],
    ]
    
    receipt_table = Table(receipt_info, colWidths=[2*inch, 4*inch])
    receipt_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(receipt_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Member & Payment details
    payment = receipt.payment
    member = receipt.member
    
    details_data = [
        ['Member Details', ''],
        ['Name:', member.name],
        ['Phone:', member.phone],
        ['', ''],
        ['Payment Details', ''],
        ['Amount:', f"₹{payment.amount}"],
        ['Payment Method:', payment.get_payment_method_display()],
        ['Payment Date:', payment.payment_date.strftime('%d-%b-%Y')],
        ['Month:', payment.month],
        ['Status:', payment.get_status_display()],
    ]
    
    if payment.transaction_id:
        details_data.append(['Transaction ID:', payment.transaction_id])
    
    details_table = Table(details_data, colWidths=[2*inch, 4*inch])
    details_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 4), (0, 4), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ECF0F1')),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#ECF0F1')),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Total amount (highlighted)
    total_data = [
        ['Total Amount Paid:', f"₹{payment.amount}"],
    ]
    
    total_table = Table(total_data, colWidths=[4*inch, 2*inch])
    total_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER
    )
    footer_text = Paragraph(
        "<i>This is a computer-generated receipt. Thank you for your payment!</i>",
        footer_style
    )
    elements.append(footer_text)
    
    # Build PDF
    doc.build(elements)
    
    # Save to file
    pdf_content = buffer.getvalue()
    buffer.close()
    
    filename = f"receipt_{receipt.receipt_number}.pdf"
    return ContentFile(pdf_content, filename)