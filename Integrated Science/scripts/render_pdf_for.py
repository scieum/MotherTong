# -*- coding: utf-8 -*-
import os
import sys
from playwright.sync_api import sync_playwright

prefix = sys.argv[1]
label = sys.argv[2]  # 파일명용 라벨, 예: 1회차

html_path = os.path.abspath(f"output/staging/{prefix}_exam.html").replace("\\", "/")
pdf_path = os.path.abspath(f"output/staging/{prefix}_{label}_시험지.pdf")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file:///{html_path}")
    page.pdf(path=pdf_path, format="A4", print_background=True,
             margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"})
    browser.close()

print("saved", pdf_path)
