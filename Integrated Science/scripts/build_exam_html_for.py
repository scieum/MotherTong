# -*- coding: utf-8 -*-
import json
import os
import sys

prefix = sys.argv[1]      # 예: set1
round_no = sys.argv[2]    # 예: 1

with open(f"scripts/{prefix}_items.json", encoding="utf-8") as f:
    items = json.load(f)

items.sort(key=lambda it: it["n"])
total_score = sum(it["score"] for it in items)

CIRCLED = {1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤"}


def fmt_score(v):
    return f"{int(v)}" if float(v) == int(v) else f"{v}"


item_blocks = []
for it in items:
    img_path = os.path.abspath(f"output/items/{prefix}/{prefix}_{it['n']:02d}.png").replace("\\", "/")
    item_blocks.append(f'''
    <div class="item">
      <img src="file:///{img_path}" />
    </div>''')

answer_rows = []
for it in items:
    answer_rows.append(
        f"<tr><td>{it['n']}</td><td>{CIRCLED[it['answer']]}</td><td>{fmt_score(it['score'])}점</td></tr>"
    )

html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<style>
  @page {{ size: A4; margin: 14mm 12mm 16mm 12mm; }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: "Malgun Gothic", "맑은 고딕", sans-serif;
    font-size: 10pt;
    color: #111;
    margin: 0;
  }}
  .cover {{
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    page-break-after: always;
  }}
  .cover h1 {{ font-size: 26pt; margin-bottom: 6mm; }}
  .cover h2 {{ font-size: 15pt; font-weight: normal; color: #444; margin-bottom: 14mm; }}
  .cover-table {{
    border-collapse: collapse;
    font-size: 11pt;
    margin-bottom: 14mm;
  }}
  .cover-table td {{
    border: 1px solid #333;
    padding: 6px 18px;
  }}
  .cover-table td.label {{
    background: #f0f0f0;
    font-weight: bold;
    text-align: center;
  }}
  .info-box {{
    border: 2px solid #333;
    padding: 10mm 14mm;
    text-align: left;
    max-width: 130mm;
    line-height: 1.9;
    font-size: 10pt;
  }}
  .info-box .title {{ font-weight: bold; margin-bottom: 4mm; text-align:center; font-size: 11pt;}}
  .name-row {{ margin-top: 14mm; font-size: 11pt; }}
  .name-row span {{ display:inline-block; border-bottom: 1px solid #333; width: 60mm; margin-left: 4mm; }}

  .body-page {{
    column-count: 2;
    column-gap: 10mm;
    column-rule: 1px solid #ccc;
  }}
  .item {{
    break-inside: avoid;
    margin-bottom: 5mm;
  }}
  .item img {{
    width: 97%;
    display: block;
  }}
  .footnote {{
    font-size: 7.5pt;
    color: #555;
    border-top: 1px solid #999;
    margin-top: 4mm;
    padding-top: 2mm;
    break-inside: avoid;
  }}

  .answer-page h2 {{ text-align:center; margin-bottom: 8mm; }}
  table.answers {{
    border-collapse: collapse;
    width: 100%;
    font-size: 10pt;
  }}
  table.answers th, table.answers td {{
    border: 1px solid #333;
    text-align: center;
    padding: 4px 2px;
  }}
  table.answers th {{ background: #f0f0f0; }}
</style>
</head>
<body>

<div class="cover">
  <h1>통합과학 모의고사</h1>
  <h2>제 {round_no} 회</h2>
  <table class="cover-table">
    <tr><td class="label">과목</td><td>통합과학 (통합과학1·통합과학2)</td></tr>
    <tr><td class="label">문항 수 / 배점</td><td>25문항 / {fmt_score(total_score)}점</td></tr>
    <tr><td class="label">시험 시간</td><td>40분</td></tr>
  </table>
  <div class="info-box">
    <div class="title">유의 사항</div>
    1. 문제지의 해당란에 성명, 수험 번호를 정확히 기입하시오.<br/>
    2. 답안지의 해당란에 답을 정확히 표시하시오.<br/>
    3. 문제지의 표지를 넘기기 전까지는 문제 내용을 열람할 수 없습니다.<br/>
    4. 시험 종료 후 문제지와 답안지를 모두 제출하시오.
  </div>
  <div class="name-row">성명 : <span></span> &nbsp;&nbsp;&nbsp; 수험 번호 : <span></span></div>
</div>

<div class="body-page">
  {''.join(item_blocks)}
  <div class="footnote">
※ 본 문항은 각 시·도교육청 전국연합학력평가 및 마더텅 편집물을 재구성한 것으로, 교실 수업 목적의 내부 이용에 한합니다. 외부 공개, 배포, 판매를 금합니다.
  </div>
</div>

<div style="page-break-before: always;" class="answer-page">
  <h2>통합과학 모의고사 제 {round_no} 회 — 정답표</h2>
  <table class="answers">
    <tr><th>번호</th><th>정답</th><th>배점</th></tr>
    {''.join(answer_rows)}
  </table>
  <div class="footnote">
  ※ 본 문항은 각 시·도교육청 전국연합학력평가 및 마더텅 편집물을 재구성한 것으로, 교실 수업 목적의 내부 이용에 한합니다. 외부 공개, 배포, 판매를 금합니다.
  </div>
</div>

</body>
</html>
'''

os.makedirs("output/staging", exist_ok=True)
out_path = f"output/staging/{prefix}_exam.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print("saved", out_path)
