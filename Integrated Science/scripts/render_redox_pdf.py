# -*- coding: utf-8 -*-
import os
from playwright.sync_api import sync_playwright

html_path = os.path.abspath("output/staging/redox_collection.html").replace("\\", "/")
pdf_path = os.path.abspath("output/staging/통합과학 주제별 기출 문항 모음(산화와 환원).pdf")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file:///{html_path}")
    page.pdf(path=pdf_path, format="A4", print_background=True,
             margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"})
    browser.close()
print("saved", pdf_path)
