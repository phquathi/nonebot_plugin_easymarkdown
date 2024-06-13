from PIL import Image
import fitz
import markdown2
from xhtml2pdf import pisa
import re

from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension

from mdx_math import MathExtension


def markdown_to_html(md_text: str) -> str:
    html = markdown2.markdown(md_text,
                              extras=["fenced-code-blocks", "tables", "strike", "cuddled-lists", "metadata",
                                      "task_list",
                                      'code-friendly', 'footnotes', 'wiki-tables', CodeHiliteExtension(),
                                      TocExtension(),
                                      MathExtension(enable_dollar_delimiter=True)])
    html = f"""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <style type="text/css">
         @page {{
            size: A4 portrait;
            size: letter portrait;        
            @frame header_frame {{         
                -pdf-frame-content: header_content;
                left: 50pt; width: 512pt; top: 50pt; height: 40pt;
            }}
            @frame col1_frame {{            
                left: 44pt; width: 512pt; top: 90pt; height: 632pt;
            }}
            @frame footer_frame {{           
                -pdf-frame-content: footer_content;
                left: 50pt; width: 512pt; top: 772pt; height: 20pt;
            }}
        }}
        body, p{{
            font-family: STSong-Light;
            font-size: 12pt;
            word-wrap: break-word;
            white-space: pre-wrap;
            overflow-wrap: break-word;
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


def insert_manual_line_breaks(html: str) -> str:
    chinese_char_pattern = re.compile(r'[\u4e00-\u9fa5]')

    def add_break_tags(text):
        new_text = ""
        char_count = 0
        for char in text:
            new_text += char
            if chinese_char_pattern.match(char):
                char_count += 1
                if char_count >= 43:
                    new_text += '<br>'
                    char_count = 0
            else:
                char_count += 1 / 2
                if char_count >= 43:
                    new_text += '<br>'
                    char_count = 0
        return new_text
    paragraph_pattern = re.compile(r'(<p>.*?</p>)', re.DOTALL)
    paragraphs = paragraph_pattern.findall(html)

    for paragraph in paragraphs:
        modified_paragraph = add_break_tags(paragraph)
        html = html.replace(paragraph, modified_paragraph)

    return html
