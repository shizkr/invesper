import fitz # PyMuPDF

def convert_pdf_to_html(pdf_path, output_html_path):
    doc = fitz.open(pdf_path)
    html_pages = []

    for page_num, page in enumerate(doc):
        spans = []
        width = page.rect.width
        height = page.rect.height

        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        size = span["size"]
                        font = span["font"]
                        color = '#{:06x}'.format(span["color"])
                        x, y = span["origin"]

                        spans.append(
                            f'<div style="position:absolute; left:{x}px; top:{y}px; '
                            f'font-size:{size}px; color:{color}; font-family:{font};">'
                            f'{text}</div>'
                        )

        page_html = f'''
        <div style="position:relative; width:{width}px; height:{height}px; margin-bottom:50px; border:1px solid #ccc;">
            {''.join(spans)}
        </div>
        '''
        html_pages.append(page_html)

    full_html = f'''
    <html>
    <head>
    <meta charset="utf-8">
    <title>PDF to HTML</title>
    </head>
    <body style="background:#f9f9f9; font-family:sans-serif;">
        {''.join(html_pages)}
    </body>
    </html>
    '''

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"✅ HTML 파일 생성 완료: {output_html_path}")

convert_pdf_to_html("ai_invest_report_2025-07-05.pdf", "ai_invest_report_2025-07-05.html")

