"""
Reports Utilities - PDF Generation
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from datetime import date, timedelta
from django.db.models import Sum
from payments.models import Payment


def generate_income_report_pdf(gym, period='this_month'):
    """Generate income report PDF"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph(f"{gym.name}", title_style))
    elements.append(Paragraph("INCOME REPORT", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Period calculation
    today = date.today()
    if period == 'this_month':
        start_date = today.replace(day=1)
        end_date = today
        period_text = f"{today.strftime('%B %Y')}"
    elif period == 'this_year':
        start_date = today.replace(month=1, day=1)
        end_date = today
        period_text = f"Year {today.year}"
    else:
        start_date = today.replace(day=1)
        end_date = today
        period_text = "Custom Period"
    
    elements.append(Paragraph(f"Period: {period_text}", styles['Normal']))
    elements.append(Paragraph(f"Generated on: {today.strftime('%d-%b-%Y')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Get payments
    payments = Payment.objects.filter(
        gym=gym,
        payment_date__gte=start_date,
        payment_date__lte=end_date,
        status='PAID'
    )
    
    total_income = payments.aggregate(total=Sum('amount'))['total'] or 0
    total_count = payments.count()
    
    # Summary table
    summary_data = [
        ['Total Payments', str(total_count)],
        ['Total Income', f"₹{total_income}"],
    ]
    
    # Payment method breakdown
    for method, label in Payment.PAYMENT_METHOD_CHOICES:
        method_total = payments.filter(payment_method=method).aggregate(total=Sum('amount'))['total'] or 0
        method_count = payments.filter(payment_method=method).count()
        if method_count > 0:
            summary_data.append([f"{label}", f"₹{method_total} ({method_count})"])
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 1), colors.white),
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Payment details
    if payments.exists():
        elements.append(Paragraph("Payment Details", styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        
        payment_data = [['Date', 'Member', 'Amount', 'Method']]
        
        for payment in payments.order_by('-payment_date')[:50]:  # Limit to 50
            payment_data.append([
                payment.payment_date.strftime('%d-%b'),
                payment.member.name[:20],
                f"₹{payment.amount}",
                payment.get_payment_method_display()
            ])
        
        payment_table = Table(payment_data, colWidths=[1*inch, 2.5*inch, 1.5*inch, 1.5*inch])
        payment_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ECF0F1')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ]))
        
        elements.append(payment_table)
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer