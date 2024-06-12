import markdown2
from PIL import Image
import fitz
from xhtml2pdf import pisa
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension
from mdx_math import MathExtension


def markdown_to_html(md_text: str) -> str:
    html = markdown2.markdown(md_text, extras=["fenced-code-blocks", "tables", "strike", "cuddled-lists", "metadata", "task_list",
                                               'code-friendly', 'footnotes', 'wiki-tables', CodeHiliteExtension(),
                                               TocExtension(),
                                               MathExtension(enable_dollar_delimiter=True)])
    html = f"""
    <html>
    <head>
        <style>
            p{{
                font-family: STSong-Light;
            }}
            @font-face {{
                font-family: STSong-Light;             
            }}
            body {{
                font-family: STSong-Light;
                font-size: 12pt;
            }}
            @page {{
                size: A4;
                margin: 1in;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
            }}
            table, th, td {{
                border: 1px solid black;
            }}
            th, td {{
                padding: 8px;
                text-align: left;
            }}
            pre {{
                background: #f4f4f4;
                padding: 10px;
                border: 1px solid #ddd;
                overflow: auto;
            }}
            code {{
                font-family: STSong-Light;
                background: #f4f4f4;
                padding: 3px;
            }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """
    return html


def create_pdf(html: str, pdf_path: str):
    with open(pdf_path, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(html, dest=result_file, encoding="utf-8")
        if pisa_status.err:
            print(f"Error converting HTML to PDF: {pisa_status.err}")


def pdf_to_images(pdf_path: str):
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images
