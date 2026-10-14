"""
pdf_generator.py
Generates clean, professional downloadable PDF attendance reports with college branding.
"""

import io                                                 # for in-memory byte buffer
from datetime import datetime                             # for current report generation timestamp
from reportlab.lib.pagesizes import letter                # letter page size
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle # reportlab components
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # styling
from reportlab.lib import colors                          # color palette


def generate_attendance_pdf(class_name, subject, date_str, time_slot, present_rolls, algo="Round Robin", faculty_name="Prof. Deepthi Rapeti"):
    buf = io.BytesIO()                                    # create in-memory byte stream
    doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36) # document

    elements = []                                         # flowable elements list
    styles = getSampleStyleSheet()                        # default sample styles

    title_style = ParagraphStyle(                         # main title style
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),             # deep navy slate color
        alignment=1                                       # center alignment
    )

    sub_style = ParagraphStyle(                           # subtitle style
        'ReportSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#D97706'),             # warm golden amber color
        alignment=1                                       # center alignment
    )

    elements.append(Paragraph("OFFICIAL LECTURE ATTENDANCE REPORT", title_style)) # add main title
    elements.append(Paragraph("Department of Artificial Intelligence & Machine Learning", sub_style)) # add subtitle
    elements.append(Spacer(1, 14))                        # spacer

    # Info summary table with Faculty Name
    meta_data = [
        [Paragraph(f"<b>Faculty:</b> {faculty_name}", styles['Normal']), Paragraph(f"<b>Subject:</b> {subject}", styles['Normal'])],
        [Paragraph(f"<b>Class:</b> {class_name}", styles['Normal']), Paragraph(f"<b>Date:</b> {date_str}", styles['Normal'])],
        [Paragraph(f"<b>Lecture Slot:</b> {time_slot}", styles['Normal']), Paragraph(f"<b>Total Present:</b> {len(present_rolls)} Students", styles['Normal'])]
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])   # create 2-column info table
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')), # light clean background
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#CBD5E1')), # subtle slate border
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')), # inner grid
        ('TOPPADDING', (0, 0), (-1, -1), 8),              # top padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),           # bottom padding
        ('LEFTPADDING', (0, 0), (-1, -1), 12),            # left padding
    ]))
    elements.append(meta_table)                           # add info table
    elements.append(Spacer(1, 16))                        # spacer

    # Student list table
    table_rows = [["#", "Student Roll Number", "Verification Status", "Timestamp"]] # table header
    gen_time = datetime.now().strftime("%H:%M:%S")        # current timestamp
    for idx, roll in enumerate(present_rolls, start=1):   # loop over present students
        table_rows.append([str(idx), f"Roll No. {roll}", "Verified & Present", gen_time]) # add row

    if len(present_rolls) == 0:                           # if no students marked yet
        table_rows.append(["-", "No attendance records found", "Pending", "-"]) # empty placeholder

    student_table = Table(table_rows, colWidths=[40, 200, 180, 120]) # student data table
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')), # slate navy header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')), # white header text
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # bold header font
        ('FONTSIZE', (0, 0), (-1, 0), 10),                # header font size
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),            # header padding
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),            # center align table
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')), # clean border
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]), # zebra striping
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),      # body font
        ('FONTSIZE', (0, 1), (-1, -1), 9),                # body font size
        ('TOPPADDING', (0, 1), (-1, -1), 6),              # cell top padding
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),           # cell bottom padding
    ]))
    elements.append(student_table)                        # add student table
    elements.append(Spacer(1, 20))                        # spacer

    elements.append(Paragraph("<font size='8' color='#64748B'>Generated via QR Smart Attendance System • Official Academic Verification Record</font>", sub_style)) # footer

    doc.build(elements)                                   # compile PDF document
    return buf.getvalue()                                 # return raw PDF bytes
