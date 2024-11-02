import json
import re
import fitz  # PyMuPDF
import base64
from io import BytesIO

def pdf_to_html(pdf_path):
    html_content = ""
    
    pdf_document = fitz.open(pdf_path)
    
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        
        page_text = page.get_text("text")
        html_content += page_text.replace("\n", "").strip()
        
    return html_content


def html_to_json(file_path):
    html_content = pdf_to_html(file_path)

    # test_pattern = r"\d+\.\s+(.+?)\s+A\)\s+(.+?)\s+B\)\s+(.+?)\s+C\)\s+(.+?)\s+D\)\s+(.+?)(?=\d+\.)"
    
    test_pattern = r"\d+\.\s+(.+?)\s+A\)+(.+?)\s+B\)+(.+?)\s+C\)+(.+?)\s+D\)+(.+?)(?=\d+\.)"
    tests = re.findall(test_pattern, html_content, re.DOTALL)
    
    data = []
    for test in tests:
        question = test[0].strip()
        variants = [test[i].strip() for i in range(1, 5)]
        
        data.append({
            "test": question,
            "variants": variants,
            'true_answer': "A"
        })

    return data
