# -*- coding: utf-8 -*-
"""주제별 모음집 PDF 렌더링. 사용법: python scripts/render_topic_pdf.py <주제키> <파일명 라벨>"""
import os
import sys

from playwright.sync_api import sync_playwright

key, label = sys.argv[1], sys.argv[2]
html_path = os.path.abspath(f"output/staging/{key}_collection.html").replace("\\", "/")
pdf_path = os.path.abspath(f"output/staging/통합과학 주제별 기출 문항 모음({label}).pdf")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file:///{html_path}")
    page.pdf(path=pdf_path, format="A4", print_background=True,
             margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"})
    browser.close()
print("saved", pdf_path)
