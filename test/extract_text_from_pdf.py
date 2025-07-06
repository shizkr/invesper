import fitz # install pymupdf

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


pdf_text = extract_text_from_pdf("ai_invest_report_2025-07-05.pdf")

print(pdf_text)
