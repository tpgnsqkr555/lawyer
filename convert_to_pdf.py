#!/usr/bin/env python3
"""Convert test_document.txt to PDF for end-to-end testing"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

def txt_to_pdf(input_file, output_file):
    """Convert text file to PDF with proper formatting"""

    # Create PDF document
    doc = SimpleDocTemplate(output_file, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)

    # Read input text
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Setup styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=4))  # 4 = Justify

    # Split into paragraphs
    paragraphs = content.split('\n\n')

    # Build story
    story = []
    for para in paragraphs:
        if para.strip():
            # Clean up text
            cleaned_text = para.replace('\n', ' ').strip()

            # Check if it's a header (short line, possibly all caps or starts with Roman numerals)
            if len(cleaned_text) < 100 and (cleaned_text.isupper() or
                                           any(cleaned_text.startswith(x) for x in ['I.', 'II.', 'III.', 'IV.', 'V.', 'MEMORANDUM', 'RE:', 'FROM:', 'DATE:', 'TO:'])):
                p = Paragraph(cleaned_text, styles['Heading2'])
            else:
                p = Paragraph(cleaned_text, styles['BodyText'])

            story.append(p)
            story.append(Spacer(1, 0.2 * inch))

    # Build PDF
    doc.build(story)
    print(f"[SUCCESS] PDF created: {output_file}")

if __name__ == "__main__":
    # Convert all three test cases
    txt_to_pdf('/Users/sehpark/Downloads/litigation/test_case_biogenesis.txt',
               '/Users/sehpark/Downloads/litigation/test_case_biogenesis.pdf')

    txt_to_pdf('/Users/sehpark/Downloads/litigation/test_case_techcorp_employment.txt',
               '/Users/sehpark/Downloads/litigation/test_case_techcorp_employment.pdf')

    txt_to_pdf('/Users/sehpark/Downloads/litigation/test_case_megamerge_ma.txt',
               '/Users/sehpark/Downloads/litigation/test_case_megamerge_ma.pdf')
