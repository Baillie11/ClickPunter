"""
PDF Exporter for ClickPunter Betting History
Generates formatted PDF reports with race details, selections, and results.
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime
import json


def generate_betting_history_pdf(bets, user_name="User"):
    """
    Generate a PDF report of betting history.
    
    Args:
        bets: List of Bet objects with associated Race and Horse data
        user_name: Name of the user for the report header
        
    Returns:
        BytesIO object containing the PDF data
    """
    # Create PDF buffer
    buffer = BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c5f2d'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c5f2d'),
        spaceAfter=6,
        spaceBefore=12
    )
    
    normal_style = styles['Normal']
    
    # Add title
    title = Paragraph("ClickPunter - Betting History Report", title_style)
    elements.append(title)
    
    # Add generation date and user
    date_text = f"Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    elements.append(Paragraph(date_text, normal_style))
    elements.append(Paragraph(f"User: {user_name}", normal_style))
    elements.append(Spacer(1, 12))
    
    # Initialize summary totals
    total_staked = 0
    total_est_return = 0
    pending_count = 0
    won_count = 0
    lost_count = 0
    
    # Group bets by date and track
    current_date = None
    current_track = None
    
    for bet in bets:
        race = bet.race
        
        # Check if we need a new date/track header
        if current_date != race.date or current_track != race.track:
            if current_date is not None:
                elements.append(Spacer(1, 12))
            
            current_date = race.date
            current_track = race.track
            
            # Add date and track header
            header_text = f"{race.date.strftime('%A, %d %B %Y')} - {race.track if race.track else 'Unknown Track'}"
            elements.append(Paragraph(header_text, heading_style))
            elements.append(Spacer(1, 6))
        
        # Parse breakdown JSON
        try:
            breakdown = json.loads(bet.breakdown_json) if bet.breakdown_json else {}
        except:
            breakdown = {}
        
        # Create bet details table
        bet_data = [
            ['Race Number:', f"Race {race.race_number}"],
            ['Selections:', ''],
            ['  A:', bet.a_horse.name if bet.a_horse else 'N/A'],
            ['  B:', bet.b_horse.name if bet.b_horse else 'N/A'],
            ['  C:', bet.c_horse.name if bet.c_horse else 'N/A'],
            ['Strategy:', bet.strategy_type or 'N/A'],
            ['Total Stake:', f"${bet.stake_total:.2f}" if bet.stake_total else 'N/A'],
        ]
        
        # Add bet breakdown if available
        if breakdown:
            bet_data.append(['Bet Breakdown:', ''])
            for bet_type, amount in breakdown.items():
                if isinstance(amount, (int, float)) and amount > 0:
                    bet_data.append([f"  {bet_type}:", f"${amount:.2f}"])
        
        # Add estimated returns
        if bet.est_total_return:
            bet_data.append(['Est. Total Return:', f"${bet.est_total_return:.2f}"])
            bet_data.append(['Est. Profit/Loss:', f"${bet.est_total_return - (bet.stake_total or 0):.2f}"])
        
        # Add status
        status = bet.result_status or 'pending'
        status_color = {
            'pending': 'Orange',
            'won': 'Green', 
            'lost': 'Red'
        }.get(status, 'Black')
        
        bet_data.append(['Status:', status.upper()])
        
        # Create table
        bet_table = Table(bet_data, colWidths=[45*mm, 70*mm])
        bet_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(bet_table)
        elements.append(Spacer(1, 10))
        
        # Update summary totals
        if bet.stake_total:
            total_staked += bet.stake_total
        if bet.est_total_return:
            total_est_return += bet.est_total_return
            
        if status == 'pending':
            pending_count += 1
        elif status == 'won':
            won_count += 1
        elif status == 'lost':
            lost_count += 1
    
    # Add summary section
    elements.append(PageBreak())
    elements.append(Paragraph("Summary", title_style))
    elements.append(Spacer(1, 12))
    
    summary_data = [
        ['Total Bets:', str(len(bets))],
        ['Pending:', str(pending_count)],
        ['Won:', str(won_count)],
        ['Lost:', str(lost_count)],
        ['', ''],
        ['Total Staked:', f"${total_staked:.2f}"],
        ['Est. Total Returns:', f"${total_est_return:.2f}"],
        ['Est. Profit/Loss:', f"${total_est_return - total_staked:.2f}"],
    ]
    
    summary_table = Table(summary_data, colWidths=[60*mm, 60*mm])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (0, 5), (-1, 5), 1, colors.grey),
        ('LINEABOVE', (0, 7), (-1, 7), 2, colors.HexColor('#2c5f2d')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Add footer
    footer_text = "Powered by Click eCommerce - www.clickecommerce.com.au"
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf
