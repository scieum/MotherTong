# -*- coding: utf-8 -*-
"""산화·환원 문항 모음집 HTML 생성 (조판 규칙은 build_exam_html_for.py를 따른다)."""
import json
import os

CIRCLED = {1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤"}
GRADE = {"고1": "고1", "고2": "고2"}

man = json.load(open("scripts/redox_manifest.json", encoding="utf-8"))


def source_label(m):
    s = m["stem"]
    if s.startswith("2028"):
        return f"{s.replace('-', ' ')} {m['label']}"
    year, month, grade, subject = s.split("-")
    return f"{year} {month} {grade} {subject} {m['orig_no']}번"


def blocks(tier):
    out = []
    for m in man:
        if m["tier"] != tier:
            continue
        p = os.path.abspath(m["png"]).replace("\\", "/")
        out.append(f'''
    <div class="item">
      <div class="src">{source_label(m)}</div>
      <img src="file:///{p}" />
    </div>''')
    return "".join(out)


def rows(tier):
    out = []
    for m in man:
        if m["tier"] != tier:
            continue
        ans = CIRCLED[m["answer"]] if m["answer"] else '<span class="na">미확보</span>'
        out.append(f"<tr><td>{m['seq']}</td><td>{source_label(m)}</td>"
                   f"<td class='topic'>{m['topic']}</td><td>{ans}</td></tr>")
    return "".join(out)


nA = sum(1 for m in man if m["tier"] == "A")
nB = sum(1 for m in man if m["tier"] == "B")

FOOT = ("※ 본 문항은 각 시·도교육청 전국연합학력평가 및 한국교육과정평가원 예시문항을 "
        "재구성한 것으로, 교실 수업 목적의 내부 이용에 한합니다. 외부 공개, 배포, 판매를 금합니다.")

html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<style>
  @page {{ size: A4; margin: 14mm 12mm 16mm 12mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: "Malgun Gothic", "맑은 고딕", sans-serif; font-size: 10pt; color: #111; margin: 0; }}

  .cover {{ height: 100vh; display: flex; flex-direction: column; justify-content: center;
            align-items: center; text-align: center; page-break-after: always; }}
  .cover h1 {{ font-size: 24pt; margin-bottom: 5mm; }}
  .cover h2 {{ font-size: 13pt; font-weight: normal; color: #444; margin-bottom: 12mm; }}
  .cover-table {{ border-collapse: collapse; font-size: 10.5pt; margin-bottom: 12mm; }}
  .cover-table td {{ border: 1px solid #333; padding: 6px 16px; }}
  .cover-table td.label {{ background: #f0f0f0; font-weight: bold; text-align: center; }}
  .note {{ border: 1px solid #999; padding: 7mm 10mm; text-align: left; max-width: 140mm;
           line-height: 1.8; font-size: 9.5pt; color: #333; }}
  .note b {{ color: #111; }}

  h2.section {{ font-size: 13pt; border-left: 5px solid #333; padding-left: 4mm;
                margin: 0 0 5mm; page-break-after: avoid; }}
  h2.section .sub {{ font-size: 9.5pt; font-weight: normal; color: #555; margin-left: 3mm; }}

  .body-page {{ column-count: 2; column-gap: 10mm; column-rule: 1px solid #ccc; }}
  .item {{ break-inside: avoid; margin-bottom: 6mm; }}
  .item .src {{ font-size: 7.5pt; color: #666; margin-bottom: 1mm; }}
  .item img {{ width: 97%; display: block; }}

  .footnote {{ font-size: 7.5pt; color: #555; border-top: 1px solid #999;
               margin-top: 4mm; padding-top: 2mm; break-inside: avoid; }}

  table.answers {{ border-collapse: collapse; width: 100%; font-size: 9pt; }}
  table.answers th, table.answers td {{ border: 1px solid #333; text-align: center; padding: 3px 4px; }}
  table.answers th {{ background: #f0f0f0; }}
  table.answers td.topic {{ text-align: left; }}
  table.answers .na {{ color: #b00; }}
  table.answers tr.head td {{ background: #e8e8e8; font-weight: bold; text-align: left; }}
</style>
</head>
<body>

<div class="cover">
  <h1>통합과학 주제별 기출 문항 모음</h1>
  <h2>산화와 환원 [10통과2-01-03]</h2>
  <table class="cover-table">
    <tr><td class="label">수록 문항</td><td>{len(man)}문항 (핵심 {nA} · 부분 연관 {nB})</td></tr>
    <tr><td class="label">출처 범위</td><td>2018~2026 전국연합학력평가 + 2028 수능 예시문항</td></tr>
    <tr><td class="label">수록 과목</td><td>통합과학 · 화학Ⅰ · 생명과학Ⅰ</td></tr>
  </table>
  <div class="note">
    <b>수록 기준</b><br/>
    · <b>Ⅰ. 핵심 문항</b> — 문항의 주된 물음이 산화·환원인 것(반응 판별, 전자 이동,
      금속의 산화와 반응성, 제련 등)<br/>
    · <b>Ⅱ. 부분 연관 문항</b> — 주제는 다른 단원이지만 &lt;보기&gt; 일부가 산화·환원 판별을 묻는 것<br/>
    · 원본 문항 번호는 수록 번호로 바꾸었고, <b>배점은 원본 표기를 그대로</b> 두었습니다.
  </div>
</div>

<h2 class="section">Ⅰ. 핵심 문항 <span class="sub">산화·환원을 직접 묻는 문항 {nA}문항</span></h2>
<div class="body-page">
  {blocks("A")}
  <div class="footnote">{FOOT}</div>
</div>

<div style="page-break-before: always;">
<h2 class="section">Ⅱ. 부분 연관 문항 <span class="sub">&lt;보기&gt; 일부가 산화·환원을 묻는 문항 {nB}문항</span></h2>
<div class="body-page">
  {blocks("B")}
  <div class="footnote">{FOOT}</div>
</div>
</div>

<div style="page-break-before: always;">
  <h2 class="section">정답 및 출처</h2>
  <table class="answers">
    <tr><th style="width:8%">번호</th><th style="width:30%">원본 출처</th>
        <th>주제</th><th style="width:8%">정답</th></tr>
    <tr class="head"><td colspan="4">Ⅰ. 핵심 문항</td></tr>
    {rows("A")}
    <tr class="head"><td colspan="4">Ⅱ. 부분 연관 문항</td></tr>
    {rows("B")}
  </table>
  <div class="footnote">
    ※ 2022년 11월 고1 통합과학은 <b>해설 PDF가 자료에 없어</b> 해당 문항의 정답을 확인하지 못했습니다.<br/>
    {FOOT}
  </div>
</div>

</body>
</html>
'''

os.makedirs("output/staging", exist_ok=True)
out = "output/staging/redox_collection.html"
open(out, "w", encoding="utf-8").write(html)
print("saved", out, "| 문항", len(man))
