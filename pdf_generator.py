import io                                                 # byte buffer for in-memory pdf
from datetime import datetime                             # generation timestamp
from reportlab.lib.pagesizes import letter                # page dimensions
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle # pdf flowables
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # typography styles
from reportlab.lib import colors                          # reportlab color palette


def generate_attendance_pdf(class_name, subject, date_str, time_slot, present_rolls, faculty_name="Ms. Seema Nagrani"):
    buffer = io.BytesIO()                                 # in-memory buffer
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36) # document setup
    elements = []                                         # flowable items list
    styles = getSampleStyleSheet()                        # stylesheet

    title_style = ParagraphStyle(                         # title typography
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.black,                           # solid black text
        alignment=1                                       # center align
    )

    subtitle_style = ParagraphStyle(                      # subtitle typography
        'ReportSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.black,                           # solid black text
        alignment=1                                       # center align
    )

    elements.append(Paragraph("OFFICIAL LECTURE ATTENDANCE REPORT", title_style)) # report title
    elements.append(Paragraph("Department of Artificial Intelligence & Machine Learning", subtitle_style)) # department subtitle
    elements.append(Spacer(1, 14))                        # vertical spacing

    info_data = [                                         # lecture metadata table
        [Paragraph(f"<b>Faculty:</b> {faculty_name}", styles['Normal']), Paragraph(f"<b>Subject:</b> {subject}", styles['Normal'])],
        [Paragraph(f"<b>Class:</b> {class_name}", styles['Normal']), Paragraph(f"<b>Date:</b> {date_str}", styles['Normal'])],
        [Paragraph(f"<b>Lecture Slot:</b> {time_slot}", styles['Normal']), Paragraph(f"<b>Total Present:</b> {len(present_rolls)} Students", styles['Normal'])]
    ]
    info_table = Table(info_data, colWidths=[270, 270])   # 2-column info grid
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),   # white background
        ('BOX', (0, 0), (-1, -1), 1.0, colors.black),     # solid black border
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black), # solid black divider
        ('TOPPADDING', (0, 0), (-1, -1), 7),              # cell padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),           # cell padding
        ('LEFTPADDING', (0, 0), (-1, -1), 12),            # left margin
    ]))
    elements.append(info_table)                           # add info card
    elements.append(Spacer(1, 16))                        # vertical spacing

    headers = ["#", "Student Roll Number", "Verification Status", "Timestamp"] # table columns
    rows = [headers]                                      # initialize rows
    recorded_time = datetime.now().strftime("%H:%M:%S")    # report timestamp

    for index, roll in enumerate(present_rolls, start=1):
        rows.append([str(index), f"Roll No. {roll}", "Verified & Present", recorded_time]) # present row

    if len(present_rolls) == 0:
        rows.append(["-", "No attendance records recorded", "Pending", "-"]) # empty placeholder

    student_table = Table(rows, colWidths=[40, 200, 180, 120]) # student roll table
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),    # solid black header box
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),     # white text on black header
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # bold headers
        ('FONTSIZE', (0, 0), (-1, 0), 10),                # font size
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),            # padding
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),            # center text
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),    # black grid lines
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white]), # pure white rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),      # body font
        ('FONTSIZE', (0, 1), (-1, -1), 9),                # body font size
        ('TOPPADDING', (0, 1), (-1, -1), 6),              # row padding
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),           # row padding
    ]))
    elements.append(student_table)                        # add table
    elements.append(Spacer(1, 20))                        # vertical spacing

    footer_style = ParagraphStyle(                        # footer typography
        'FooterText',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.black,                           # black footer text
        alignment=1
    )
    elements.append(Paragraph("Generated via Smart QR Attendance System • Verified Academic Record", footer_style)) # footer

    doc.build(elements)                                   # compile pdf
    return buffer.getvalue()                              # return raw pdf bytes
