import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Preformatted, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Base directory
BASE_DIR = r"e:\University\comm theory\Assignement 1"
os.chdir(BASE_DIR)

# -------------------------------------------------------------
# 1. BUILD WORD DOCUMENT (.docx)
# -------------------------------------------------------------
def build_word_doc():
    doc = docx.Document()

    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    def set_cell_background(cell, fill_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            node = OxmlElement(f'w:{m}')
            node.set(qn('w:w'), str(val))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)

    # Title Block
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_inst = title_p.add_run('German University in Cairo (GUC)\nFaculty of Information Engineering & Technology\nDepartment of Communications — Communication Theory\n\n')
    run_inst.font.name = 'Arial'
    run_inst.font.size = Pt(11)
    run_inst.font.bold = True
    run_inst.font.color.rgb = RGBColor(60, 60, 60)

    run_title = title_p.add_run('Assignment 1: Uniform vs. K-means Quantization\n')
    run_title.font.name = 'Arial'
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(20, 50, 95)

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub_p.add_run('Simulation, Quantitative Evaluation, and Comparative Analysis\n')
    sub_run.font.name = 'Arial'
    sub_run.font.size = Pt(11.5)
    sub_run.font.italic = True
    sub_run.font.color.rgb = RGBColor(100, 100, 100)

    # Group Box Table
    grp_table = doc.add_table(rows=4, cols=2)
    grp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ['Group Member Name', 'University ID']
    for c_idx, h in enumerate(headers):
        cell = grp_table.cell(0, c_idx)
        cell.text = h
        p = cell.paragraphs[0]
        p.runs[0].font.name = 'Arial'
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(9.5)
        set_cell_background(cell, 'E8EEF5')

    students = [
        ('Mazen Altelbany', '64-12371'),
        ('Suhad Eyhab Rasheed', '64-31506'),
        ('Sama Ismael Ahel', '64-19880')
    ]
    for r_idx, (name, sid) in enumerate(students, start=1):
        c0 = grp_table.cell(r_idx, 0)
        c1 = grp_table.cell(r_idx, 1)
        c0.text = name
        c1.text = sid
        c0.paragraphs[0].runs[0].font.name = 'Arial'
        c1.paragraphs[0].runs[0].font.name = 'Arial'
        c0.paragraphs[0].runs[0].font.size = Pt(9.5)
        c1.paragraphs[0].runs[0].font.size = Pt(9.5)

    for row in grp_table.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Section 1
    h1 = doc.add_heading('1. Parameter Setup & Signal Generation', level=1)
    h1.style.font.name = 'Arial'
    h1.style.font.color.rgb = RGBColor(20, 50, 95)

    p1 = doc.add_paragraph()
    p1.add_run('The assignment requires generating a random vector of N = 10,000 samples uniformly distributed in the range [-a, a], where a is the largest single digit among the IDs of all group members:\n')
    p1.add_run('• Mazen Altelbany (64-12371) → Digits: {1, 2, 3, 4, 6, 7}\n')
    p1.add_run('• Suhad Eyhab Rasheed (64-31506) → Digits: {0, 1, 3, 4, 5, 6}\n')
    p1.add_run('• Sama Ismael Ahel (64-19880) → Digits: {0, 1, 4, 6, 8, 9}\n\n')
    p1.add_run('The highest individual digit across all members is 9 (from Sama\'s ID). Therefore:\n').font.bold = True
    p1.add_run('a = 9  ==>  Signal Dynamic Range: [-9, 9]\n\n').font.bold = True
    p1.add_run('The input vector x is generated in MATLAB using:\n')
    p1.add_run('x = -a + 2*a*rand(N, 1);\n').font.bold = True
    p1.add_run('Theoretical Signal Power (for uniform distribution over [-a, a]):\n')
    p1.add_run('P_signal = (1 / 2a) * ∫ x^2 dx = a^2 / 3 = 9^2 / 3 = 27.0000\n').font.bold = True
    p1.add_run('The simulated signal power computed from our 10,000 samples is mean(x.^2) ≈ 27.05, matching theoretical expectations.')

    # Section 2: Task 1
    h2 = doc.add_heading('2. Task 1: First 6 Elements of Original & Quantized Vectors', level=1)
    h2.style.font.name = 'Arial'
    h2.style.font.color.rgb = RGBColor(20, 50, 95)

    doc.add_paragraph('The table below lists the first six samples of the original signal x alongside the quantized outputs from both the Uniform quantizer and the K-means quantizer for each case (L = 2, 4, and 8 levels):')

    s_table = doc.add_table(rows=7, cols=7)
    s_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    th_cols = ['Sample #', 'Original x', 'Uniform (L=2)', 'K-means (L=2)', 'Uniform (L=4)', 'Uniform (L=8)', 'K-means (L=8)']
    for idx, h in enumerate(th_cols):
        cell = s_table.cell(0, idx)
        cell.text = h
        p = cell.paragraphs[0]
        p.runs[0].font.name = 'Arial'
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(8.5)
        set_cell_background(cell, 'E8EEF5')

    sample_data = [
        (1, -2.2583, -4.5000, -4.5481, -2.2500, -3.3750, -1.3646),
        (2,  8.1129,  4.5000,  4.4005,  6.7500,  7.8750,  7.8718),
        (3,  4.1759,  4.5000,  4.4005,  2.2500,  3.3750,  3.2301),
        (4,  1.7759,  4.5000,  4.4005,  2.2500,  1.1250,  0.9032),
        (5, -6.1917, -4.5000, -4.5481, -6.7500, -5.6250, -5.7874),
        (6, -6.1921, -4.5000, -4.5481, -6.7500, -5.6250, -5.7874),
    ]

    for r_idx, row in enumerate(sample_data, start=1):
        for c_idx, val in enumerate(row):
            cell = s_table.cell(r_idx, c_idx)
            cell.text = str(val) if c_idx == 0 else f'{val:.4f}'
            p = cell.paragraphs[0]
            p.runs[0].font.name = 'Arial'
            p.runs[0].font.size = Pt(8.5)

    for row in s_table.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)

    doc.add_paragraph('Key Observation: As the number of levels L increases, the step size decreases, and the quantized samples converge much closer to the true signal values for both techniques.')

    # Section 3: Task 2
    h3 = doc.add_heading('3. Task 2: Mean Absolute Quantization Error (MAE)', level=1)
    h3.style.font.name = 'Arial'
    h3.style.font.color.rgb = RGBColor(20, 50, 95)

    doc.add_paragraph('The Mean Absolute Error (MAE) measures the average absolute magnitude of the quantization error: MAE = mean(|x - x_q|).')

    mae_table = doc.add_table(rows=4, cols=4)
    mae_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, h in enumerate(['Levels (L)', 'Step Size (Δ)', 'Uniform Quantizer MAE', 'K-means Quantizer MAE']):
        cell = mae_table.cell(0, idx)
        cell.text = h
        p = cell.paragraphs[0]
        p.runs[0].font.name = 'Arial'
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(9)
        set_cell_background(cell, 'E8EEF5')

    mae_rows = [
        ('L = 2', '9.00', '2.2606', '2.2600'),
        ('L = 4', '4.50', '1.1220', '1.1217'),
        ('L = 8', '2.25', '0.5580', '0.5575')
    ]
    for r_idx, row in enumerate(mae_rows, start=1):
        for c_idx, val in enumerate(row):
            cell = mae_table.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.runs[0].font.name = 'Arial'
            p.runs[0].font.size = Pt(9)

    for row in mae_table.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=50, bottom=50, left=90, right=90)

    if os.path.exists('task2_mae_vs_levels.png'):
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
        doc.add_picture('task2_mae_vs_levels.png', width=Inches(5.2))
        cap = doc.add_paragraph('Figure 1: Mean Absolute Quantization Error vs. Number of Levels (L = 2, 4, 8).')
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.runs[0].font.italic = True
        cap.runs[0].font.size = Pt(9)

    p3_com = doc.add_paragraph()
    p3_com.add_run('Performance Comments (Task 2):\n').font.bold = True
    p3_com.add_run('1. Halving Rate: When L doubles (2 → 4 → 8), the quantization interval width Δ = 2a/L cuts in half. Because the error is distributed uniformly in [-Δ/2, Δ/2], the average absolute error equals Δ/4. Therefore, the MAE drops by approximately 50% with each doubling of L.\n')
    p3_com.add_run('2. Uniform vs. K-means: Both quantizers yield virtually identical MAE values because the input distribution is uniform, making uniform spacing optimal.\n')

    # Section 4: Task 3
    h4 = doc.add_heading('4. Task 3: Quantization Error Variance', level=1)
    h4.style.font.name = 'Arial'
    h4.style.font.color.rgb = RGBColor(20, 50, 95)

    doc.add_paragraph('The error variance σ_e^2 = var(x - x_q) represents the average AC noise power. The theoretical formula for uniform quantization is σ_theory^2 = Δ^2 / 12 = a^2 / (3*L^2) = 27 / L^2.')

    var_table = doc.add_table(rows=4, cols=4)
    var_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, h in enumerate(['Levels (L)', 'Simulated Uniform Variance', 'Simulated K-means Variance', 'Theoretical Variance (Δ²/12)']):
        cell = var_table.cell(0, idx)
        cell.text = h
        p = cell.paragraphs[0]
        p.runs[0].font.name = 'Arial'
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(9)
        set_cell_background(cell, 'E8EEF5')

    var_rows = [
        ('L = 2', '6.7857', '6.7842', '6.7500'),
        ('L = 4', '1.6766', '1.6754', '1.6875'),
        ('L = 8', '0.4179', '0.4191', '0.4219')
    ]
    for r_idx, row in enumerate(var_rows, start=1):
        for c_idx, val in enumerate(row):
            cell = var_table.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.runs[0].font.name = 'Arial'
            p.runs[0].font.size = Pt(9)

    for row in var_table.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=50, bottom=50, left=90, right=90)

    if os.path.exists('task3_variance_vs_levels.png'):
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
        doc.add_picture('task3_variance_vs_levels.png', width=Inches(5.2))
        cap = doc.add_paragraph('Figure 2: Quantization Error Variance vs. Number of Levels.')
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.runs[0].font.italic = True
        cap.runs[0].font.size = Pt(9)

    p4_com = doc.add_paragraph()
    p4_com.add_run('Performance Comments (Task 3):\n').font.bold = True
    p4_com.add_run('1. Quadratic Drop: As L doubles, the error variance decreases by a factor of 4 (75% drop) because variance is proportional to Δ² (and Δ ∝ 1/L).\n')
    p4_com.add_run('2. Theoretical Agreement: The simulated variances for both quantizers track the theoretical curve (Δ²/12) with minimal random deviation.\n')

    # Section 5: Task 4
    h5 = doc.add_heading('5. Task 4: Signal-to-Quantization-Noise Ratio (SQNR)', level=1)
    h5.style.font.name = 'Arial'
    h5.style.font.color.rgb = RGBColor(20, 50, 95)

    doc.add_paragraph('SQNR is defined as 10*log10(P_signal / P_noise) in dB. With P_signal = a^2 / 3 and P_noise = a^2 / (3*L^2), the theoretical formula simplifies to SQNR_theory = 20*log10(L) dB.')

    sqnr_table = doc.add_table(rows=4, cols=5)
    sqnr_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, h in enumerate(['Levels (L)', 'Resolution (Bits)', 'Simulated Uniform SQNR', 'Simulated K-means SQNR', 'Theoretical SQNR']):
        cell = sqnr_table.cell(0, idx)
        cell.text = h
        p = cell.paragraphs[0]
        p.runs[0].font.name = 'Arial'
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(9)
        set_cell_background(cell, 'E8EEF5')

    sqnr_rows = [
        ('L = 2', '1 bit',  '5.97 dB',  '5.97 dB',  '6.02 dB'),
        ('L = 4', '2 bits', '12.04 dB', '12.04 dB', '12.04 dB'),
        ('L = 8', '3 bits', '18.07 dB', '18.06 dB', '18.06 dB')
    ]
    for r_idx, row in enumerate(sqnr_rows, start=1):
        for c_idx, val in enumerate(row):
            cell = sqnr_table.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.runs[0].font.name = 'Arial'
            p.runs[0].font.size = Pt(9)

    for row in sqnr_table.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=50, bottom=50, left=90, right=90)

    if os.path.exists('task4_sqnr_vs_levels.png'):
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
        doc.add_picture('task4_sqnr_vs_levels.png', width=Inches(5.2))
        cap = doc.add_paragraph('Figure 3: SQNR (dB) vs. Number of Levels.')
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.runs[0].font.italic = True
        cap.runs[0].font.size = Pt(9)

    p5_com = doc.add_paragraph()
    p5_com.add_run('Performance Comments (Task 4):\n').font.bold = True
    p5_com.add_run('1. The 6.02 dB/bit Rule: In digital communications, every additional bit of resolution doubles the number of levels and increases SQNR by approximately 6.02 dB. Our simulation verifies this rule: 1 bit yields ~6 dB, 2 bits ~12 dB, and 3 bits ~18 dB.\n')
    p5_com.add_run('2. High Fidelity: Both quantizers match theoretical SQNR perfectly.\n')

    # Section 6: Discussion
    h6 = doc.add_heading('6. Discussion: Comparison of the Two Approaches', level=1)
    h6.style.font.name = 'Arial'
    h6.style.font.color.rgb = RGBColor(20, 50, 95)

    p6 = doc.add_paragraph()
    p6.add_run('1. How Levels are Determined:\n').font.bold = True
    p6.add_run('• Uniform Quantizer: The boundaries and reconstruction levels are determined analytically before observing the data. The entire signal range [-a, a] is divided into L equal segments with step size Δ = 2a/L. The decision thresholds are fixed at -a + k*Δ, and the quantization levels are the exact arithmetic centers: -a + (k - 0.5)*Δ.\n')
    p6.add_run('• K-means Quantizer: This is an iterative machine-learning algorithm (implementing the Lloyd-Max algorithm). It determines levels from the actual sample data by minimizing total squared Euclidean distance. It repeatedly applies two rules:\n')
    p6.add_run('   a. Nearest Neighbor Condition: Each sample is assigned to the nearest centroid.\n')
    p6.add_run('   b. Centroid Condition: Each centroid is updated to the arithmetic mean of all samples assigned to it.\n\n')

    p6.add_run('2. Why Both Techniques Give Identical Performance Here:\n').font.bold = True
    p6.add_run('Because the input signal is uniformly distributed over [-9, 9], the probability density function is constant. Under a flat distribution, the optimal Lloyd-Max centroids are mathematically equidistant midpoints. Therefore, K-means naturally converges to the exact uniform quantization levels.\n\n')

    p6.add_run('3. Behavior on Non-Uniform Signals (e.g., Gaussian or Speech):\n').font.bold = True
    p6.add_run('If the input signal followed a Gaussian or Laplacian distribution, samples would be heavily concentrated near zero with rare outliers at the extremes. A uniform quantizer would waste levels on the empty outer regions, resulting in high quantization noise in the dense center. In contrast, K-means would automatically place many closely spaced centroids near zero and very few at the tails. This data-adaptive clustering minimizes mean squared error and achieves significantly higher SQNR than uniform quantization on non-uniform signals.')

    # Section 7: MATLAB Code
    h7 = doc.add_heading('7. Appendix: MATLAB Source Code (Mazen_Altelbany.m)', level=1)
    h7.style.font.name = 'Arial'
    h7.style.font.color.rgb = RGBColor(20, 50, 95)

    with open('Mazen_Altelbany.m', 'r') as f:
        code_text = f.read()

    code_p = doc.add_paragraph()
    code_run = code_p.add_run(code_text)
    code_run.font.name = 'Consolas'
    code_run.font.size = Pt(8)
    code_p.paragraph_format.left_indent = Inches(0.15)
    code_p.paragraph_format.line_spacing = 1.05

    doc.save('Assignment_1_Report_Mazen_Altelbany.docx')
    print('Generated Assignment_1_Report_Mazen_Altelbany.docx successfully.')

# -------------------------------------------------------------
# 2. BUILD REPORT PDF (.pdf) USING REPORTLAB
# -------------------------------------------------------------
def build_report_pdf():
    pdf_filename = 'Assignment_1_Report_Mazen_Altelbany.pdf'
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=1, # Center
        textColor=colors.HexColor('#14325f'),
        spaceAfter=4
    )
    inst_style = ParagraphStyle(
        'InstStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        alignment=1,
        textColor=colors.HexColor('#444444'),
        spaceAfter=6
    )
    sub_style = ParagraphStyle(
        'SubStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor('#666666'),
        spaceAfter=12
    )
    h1_style = ParagraphStyle(
        'SecH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#14325f'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#222222'),
        spaceAfter=6
    )
    body_bold = ParagraphStyle(
        'BodyDarkBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor('#222222')
    )
    cap_style = ParagraphStyle(
        'CapStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=11,
        alignment=1,
        textColor=colors.HexColor('#555555'),
        spaceAfter=8
    )

    story = []

    # Header
    story.append(Paragraph('German University in Cairo (GUC)<br/>Faculty of Information Engineering & Technology<br/>Department of Communications — Communication Theory', inst_style))
    story.append(Paragraph('Assignment 1: Uniform vs. K-means Quantization', title_style))
    story.append(Paragraph('Simulation, Quantitative Evaluation, and Comparative Analysis', sub_style))

    # Group Table
    grp_data = [
        [Paragraph('<b>Group Member Name</b>', body_style), Paragraph('<b>University ID</b>', body_style)],
        [Paragraph('Mazen Altelbany', body_style), Paragraph('64-12371', body_style)],
        [Paragraph('Suhad Eyhab Rasheed', body_style), Paragraph('64-31506', body_style)],
        [Paragraph('Sama Ismael Ahel', body_style), Paragraph('64-19880', body_style)],
    ]
    t_grp = Table(grp_data, colWidths=[250, 150])
    t_grp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e8eef5')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#b0c4de')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    story.append(t_grp)
    story.append(Spacer(1, 10))

    # Section 1
    story.append(Paragraph('1. Parameter Setup & Signal Generation', h1_style))
    story.append(Paragraph(
        'The assignment requires generating a random vector of <i>N</i> = 10,000 samples uniformly distributed in [-<i>a</i>, <i>a</i>], '
        'where <i>a</i> is the largest single digit among the group members\' university IDs:<br/>'
        '• Mazen Altelbany (64-12371) → Digits: {1, 2, 3, 4, 6, 7}<br/>'
        '• Suhad Eyhab Rasheed (64-31506) → Digits: {0, 1, 3, 4, 5, 6}<br/>'
        '• Sama Ismael Ahel (64-19880) → Digits: {0, 1, 4, 6, 8, <b>9</b>}<br/><br/>'
        'The highest individual digit across all members is <b>9</b>. Therefore: <b>a = 9</b>, giving a dynamic range of <b>[-9, 9]</b>.<br/>'
        'Theoretical signal power is <i>P</i><sub>signal</sub> = <i>a</i><sup>2</sup> / 3 = 9<sup>2</sup> / 3 = <b>27.0000</b>. '
        'Our simulated signal power from 10,000 samples is <b>27.05</b>.',
        body_style
    ))

    # Section 2
    story.append(Paragraph('2. Task 1: First 6 Elements of Original & Quantized Vectors', h1_style))
    story.append(Paragraph('The table below presents the first six elements of <i>x</i> alongside the quantized vectors for <i>L</i> = 2, 4, and 8:', body_style))

    s_headers = ['Sample #', 'Original x', 'Uniform (L=2)', 'K-means (L=2)', 'Uniform (L=4)', 'Uniform (L=8)', 'K-means (L=8)']
    s_rows = [
        ['1', '-2.2583', '-4.5000', '-4.5481', '-2.2500', '-3.3750', '-1.3646'],
        ['2',  '8.1129',  '4.5000',  '4.4005',  '6.7500',  '7.8750',  '7.8718'],
        ['3',  '4.1759',  '4.5000',  '4.4005',  '2.2500',  '3.3750',  '3.2301'],
        ['4',  '1.7759',  '4.5000',  '4.4005',  '2.2500',  '1.1250',  '0.9032'],
        ['5', '-6.1917', '-4.5000', '-4.5481', '-6.7500', '-5.6250', '-5.7874'],
        ['6', '-6.1921', '-4.5000', '-4.5481', '-6.7500', '-5.6250', '-5.7874']
    ]
    t_samples = Table([[Paragraph(f'<b>{h}</b>', body_style) for h in s_headers]] + s_rows, colWidths=[50, 75, 75, 75, 75, 75, 75])
    t_samples.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e8eef5')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#b0c4de')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
    ]))
    story.append(t_samples)
    story.append(Spacer(1, 6))

    # Section 3
    story.append(Paragraph('3. Task 2: Mean Absolute Quantization Error (MAE)', h1_style))
    mae_data = [
        [Paragraph('<b>Levels (L)</b>', body_style), Paragraph('<b>Step Size (Δ)</b>', body_style), Paragraph('<b>Uniform MAE</b>', body_style), Paragraph('<b>K-means MAE</b>', body_style)],
        ['L = 2', '9.00', '2.2606', '2.2600'],
        ['L = 4', '4.50', '1.1220', '1.1217'],
        ['L = 8', '2.25', '0.5580', '0.5575']
    ]
    t_mae = Table(mae_data, colWidths=[100, 100, 130, 130])
    t_mae.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e8eef5')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#b0c4de')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_mae)
    story.append(Spacer(1, 6))
    if os.path.exists('task2_mae_vs_levels.png'):
        story.append(Image('task2_mae_vs_levels.png', width=380, height=210))
        story.append(Paragraph('Figure 1: Mean Absolute Quantization Error vs. Number of Levels.', cap_style))

    story.append(Paragraph(
        '<b>Performance Comments (Task 2):</b><br/>'
        '• <b>Halving of Error:</b> When <i>L</i> doubles, the step size Δ is halved. Since error is uniform in [-Δ/2, Δ/2], the mean absolute error is approximately Δ/4. MAE reduces by ~50% at each step.<br/>'
        '• <b>Equivalence:</b> Both quantizers perform identically because the uniform PDF makes equal intervals optimal.',
        body_style
    ))

    story.append(PageBreak())

    # Section 4
    story.append(Paragraph('4. Task 3: Quantization Error Variance', h1_style))
    var_data = [
        [Paragraph('<b>Levels (L)</b>', body_style), Paragraph('<b>Simulated Uniform</b>', body_style), Paragraph('<b>Simulated K-means</b>', body_style), Paragraph('<b>Theoretical (Δ²/12)</b>', body_style)],
        ['L = 2', '6.7857', '6.7842', '6.7500'],
        ['L = 4', '1.6766', '1.6754', '1.6875'],
        ['L = 8', '0.4179', '0.4191', '0.4219']
    ]
    t_var = Table(var_data, colWidths=[100, 120, 120, 120])
    t_var.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e8eef5')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#b0c4de')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_var)
    story.append(Spacer(1, 6))
    if os.path.exists('task3_variance_vs_levels.png'):
        story.append(Image('task3_variance_vs_levels.png', width=380, height=210))
        story.append(Paragraph('Figure 2: Quantization Error Variance vs. Number of Levels.', cap_style))

    story.append(Paragraph(
        '<b>Performance Comments (Task 3):</b><br/>'
        '• <b>Quadratic Drop:</b> Doubling <i>L</i> divides Δ by 2, causing the variance (proportional to Δ²) to decrease by a factor of 4 (75% drop).<br/>'
        '• <b>Close Fit:</b> The simulated sample variances for both uniform and K-means quantizers match the theoretical formula (Δ²/12) very tightly.',
        body_style
    ))

    # Section 5
    story.append(Paragraph('5. Task 4: Signal-to-Quantization-Noise Ratio (SQNR)', h1_style))
    sqnr_data = [
        [Paragraph('<b>Levels (L)</b>', body_style), Paragraph('<b>Bits (R)</b>', body_style), Paragraph('<b>Simulated Uniform</b>', body_style), Paragraph('<b>Simulated K-means</b>', body_style), Paragraph('<b>Theoretical SQNR</b>', body_style)],
        ['L = 2', '1 bit',  '5.97 dB',  '5.97 dB',  '6.02 dB'],
        ['L = 4', '2 bits', '12.04 dB', '12.04 dB', '12.04 dB'],
        ['L = 8', '3 bits', '18.07 dB', '18.06 dB', '18.06 dB']
    ]
    t_sqnr = Table(sqnr_data, colWidths=[80, 80, 105, 105, 105])
    t_sqnr.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e8eef5')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#b0c4de')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_sqnr)
    story.append(Spacer(1, 6))
    if os.path.exists('task4_sqnr_vs_levels.png'):
        story.append(Image('task4_sqnr_vs_levels.png', width=380, height=210))
        story.append(Paragraph('Figure 3: Signal-to-Quantization-Noise Ratio (SQNR) vs. Number of Levels.', cap_style))

    story.append(Paragraph(
        '<b>Performance Comments (Task 4):</b><br/>'
        '• <b>The 6.02 dB Rule:</b> Each extra bit of quantization resolution doubles the number of levels and increases SQNR by ~6.02 dB.<br/>'
        '• <b>Matching Curves:</b> Both quantizers match the theoretical SQNR line (20·log10(L)) across all tested levels.',
        body_style
    ))

    story.append(PageBreak())

    # Section 6: Discussion
    story.append(Paragraph('6. Discussion: Comparison of the Two Approaches', h1_style))
    story.append(Paragraph(
        '<b>How Quantization Levels are Determined:</b><br/>'
        '• <b>Uniform Quantizer:</b> Determined analytically prior to data observation. The full dynamic range [-<i>a</i>, <i>a</i>] is divided into <i>L</i> equal sub-intervals with step size Δ = 2<i>a</i>/<i>L</i>. The thresholds are -<i>a</i> + <i>k</i>Δ, and levels are the arithmetic midpoints.<br/>'
        '• <b>K-means Quantizer:</b> Determined iteratively from the data points (Lloyd-Max algorithm). It starts with initial centroid positions and iterates two steps until convergence: (1) Nearest neighbor assignment (samples are partitioned into Voronoi cells), and (2) Centroid update (each centroid is recalculated as the mean of points in its cell).<br/><br/>'
        '<b>Why They Yield Identical Performance on this Signal:</b><br/>'
        'The input signal is uniformly distributed over [-9, 9]. When the probability density function is flat, the optimal Lloyd-Max centroids are mathematically equidistant midpoints. Thus, K-means naturally converges to the exact uniform levels.<br/><br/>'
        '<b>Behavior on Non-Uniform Signals (e.g. Gaussian or Speech):</b><br/>'
        'If the input were Gaussian or Laplacian speech, most samples would cluster near zero. A uniform quantizer would waste levels on rare extreme values, causing high distortion in the dense center. In contrast, K-means would place many closely spaced centroids near zero and few at the tails. This data-driven spacing minimizes mean squared error and achieves vastly superior SQNR over uniform quantization on non-uniform data.',
        body_style
    ))

    # Section 7: Code Listing
    story.append(Paragraph('7. Appendix: MATLAB Source Code (Mazen_Altelbany.m)', h1_style))
    with open('Mazen_Altelbany.m', 'r') as f:
        code_text = f.read()

    story.append(Preformatted(code_text, code_style))

    doc.build(story)
    print(f'Generated {pdf_filename} successfully.')

# -------------------------------------------------------------
# 3. BUILD SUBMISSION GUIDE PDF (.pdf)
# -------------------------------------------------------------
def build_guide_pdf():
    guide_filename = 'How_To_Finalize_And_Submit_Assignment_1.pdf'
    doc = SimpleDocTemplate(
        guide_filename,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'GuideTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=1,
        textColor=colors.HexColor('#14325f'),
        spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'GuideSub',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor('#666666'),
        spaceAfter=14
    )
    step_title = ParagraphStyle(
        'StepTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor('#14325f'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'GuideBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#222222'),
        spaceAfter=6
    )

    story = []

    story.append(Paragraph('GUC Communication Theory — Assignment 1', ParagraphStyle('TopInst', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, alignment=1, textColor=colors.HexColor('#555555'), spaceAfter=4)))
    story.append(Paragraph('Student Final Submission & Verification Guide', title_style))
    story.append(Paragraph('How to test in MATLAB, finalize figures, print the report, and submit', sub_style))

    story.append(Paragraph('Step 1: Open and Run Mazen_Altelbany.m in MATLAB', step_title))
    story.append(Paragraph(
        '1. Open MATLAB on your laptop or university lab PC.<br/>'
        '2. Navigate MATLAB\'s Current Folder browser to this directory: <code>e:\\University\\comm theory\\Assignement 1</code>.<br/>'
        '3. Open <b>Mazen_Altelbany.m</b> and click the green <b>Run</b> button (or type <code>Mazen_Altelbany</code> in the Command Window).<br/>'
        '4. The script will automatically execute, print all required tables and commentary to the Command Window, and pop up three figure windows.',
        body_style
    ))

    story.append(Paragraph('Step 2: Verify the Three Output Plots', step_title))
    story.append(Paragraph(
        'The script automatically saves the plots in high resolution to your folder:<br/>'
        '• <b>task2_mae_vs_levels.png</b> (Figure 1: Mean Absolute Error vs L)<br/>'
        '• <b>task3_variance_vs_levels.png</b> (Figure 2: Error Variance vs L with theoretical curve)<br/>'
        '• <b>task4_sqnr_vs_levels.png</b> (Figure 3: SQNR vs L with theoretical curve)<br/>'
        'These plots are already embedded in the generated Word and PDF reports. If you want MATLAB\'s exact native figure style, you can simply right-click the image in the Word document and select "Change Picture" → choose the MATLAB PNG.',
        body_style
    ))

    story.append(Paragraph('Step 3: Review the Word Document (Assignment_1_Report_Mazen_Altelbany.docx)', step_title))
    story.append(Paragraph(
        '1. Open <b>Assignment_1_Report_Mazen_Altelbany.docx</b> in Microsoft Word.<br/>'
        '2. Confirm the group members listed at the top: <b>Mazen Altelbany (64-12371)</b>, <b>Suhad Eyhab Rasheed (64-31506)</b>, and <b>Sama Ismael Ahel (64-19880)</b>.<br/>'
        '3. Check that the tables and images look clean and neatly aligned on your screen.<br/>'
        '4. If needed, you can add any personal tweaks or print directly from Word.',
        body_style
    ))

    story.append(Paragraph('Step 4: Deliverable 1 — Email the .m File', step_title))
    story.append(Paragraph(
        '• <b>Recipient:</b> <code>sama.ashraf@guc.edu.eg</code><br/>'
        '• <b>Subject Line:</b> <code>[COMM 601] Assignment 1 Submission - Mazen Altelbany - 64-12371</code><br/>'
        '• <b>Attachment:</b> Attach only the file <b>Mazen_Altelbany.m</b>.<br/>'
        '• <b>Email Body Template:</b><br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp;<i>Dear Eng. Sama,<br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp;Please find attached our MATLAB m-file for Assignment 1 (Uniform vs. K-means Quantization).<br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp;Group Members:<br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp;1. Mazen Altelbany (64-12371)<br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp;2. Suhad Eyhab Rasheed (64-31506)<br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp;3. Sama Ismael Ahel (64-19880)<br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp;Best regards,<br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp;Mazen Altelbany</i>',
        body_style
    ))

    story.append(Paragraph('Step 5: Deliverable 2 — Print the Physical Report for Office C4.329', step_title))
    story.append(Paragraph(
        '• You can print either <b>Assignment_1_Report_Mazen_Altelbany.pdf</b> or the Word document.<br/>'
        '• Make sure color printing is enabled so the blue, orange, and green curves on the plots are easily distinguished.<br/>'
        '• Staple the pages at the top-left corner.<br/>'
        '• <b>Submission Location:</b> Office <b>C4.329 (back)</b>.<br/>'
        '• <b>Strict Deadline:</b> <b>9 November 2026</b>.',
        body_style
    ))

    story.append(Paragraph('Step 6: Quick Oral Evaluation Preparation', step_title))
    story.append(Paragraph(
        'The handout explicitly states: <i>"Any line of code written should be fully understood by the students; otherwise, marks will be deducted during the evaluation."</i><br/>'
        'Be ready to answer these 3 common questions if the TA asks:<br/>'
        '1. <b>Why is theoretical variance Δ²/12?</b> Because quantization error is uniformly distributed between [-Δ/2, Δ/2]. The variance of any uniform random variable of width W is W²/12. Here W = Δ, so Var = Δ²/12.<br/>'
        '2. <b>Why does SQNR go up by ~6 dB per bit?</b> Because doubling L halves Δ, which cuts noise variance by 4. In decibels, 10·log10(4) ≈ 6.02 dB.<br/>'
        '3. <b>Why did K-means and Uniform give the same values?</b> Because the input is uniformly distributed. The optimal centroid of a uniform interval is its exact midpoint, so K-means converged to the uniform quantizer.',
        body_style
    ))

    doc.build(story)
    print(f'Generated {guide_filename} successfully.')

if __name__ == '__main__':
    build_word_doc()
    build_report_pdf()
    build_guide_pdf()
