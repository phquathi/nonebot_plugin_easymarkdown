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
    line_length = 42

    def add_breaks(text, line_length):
        text = text.replace("<br>", "")
        result = ""
        current_length = 0

        for char in text:
            result += char
            current_length += 1

            if current_length >= line_length:
                result += "<br>"
                current_length = 0

        return result

    def process_tags(tag_pattern, html):
        matches = tag_pattern.findall(html)
        for match in matches:
            inner_content = re.search(r'>(.*?)<', match, re.DOTALL)
            if inner_content:
                inner_text = inner_content.group(1)
                modified_text = add_breaks(inner_text, line_length)
                html = html.replace(inner_text, modified_text)
        return html

    paragraph_pattern = re.compile(r'(<p>.*?</p>)', re.DOTALL)
    html = process_tags(paragraph_pattern, html)

    li_pattern = re.compile(r'(<li>(?!<p>).*?</li>)', re.DOTALL)
    html = process_tags(li_pattern, html)

    li_with_p_pattern = re.compile(r'(<li><p>.*?</p></li>)', re.DOTALL)
    html = process_tags(li_with_p_pattern, html)

    return html
