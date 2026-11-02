# -*- coding: utf-8 -*-
"""/inbox의 모든 문제 PDF를 문항 단위로 쪼개 텍스트를 뽑아 JSON으로 저장한다.

컬럼 경계는 페이지마다 흔들리므로(같은 파일에서도 306pt/276pt로 달라짐) 쓰지 않는다.
대신 문서 전체에서 "N." 워드의 x0 히스토그램을 만들어 실제 문항 번호가 찍히는
x 위치(컬럼 왼쪽 기준선)를 먼저 확정하고, 그 위치의 번호만 문항 머리로 인정한다.
번호는 1번부터 순차적으로만 받아들여 본문 속 숫자 오인을 막는다.
"""
import json
import os
import re

import fitz

NUM_RE = re.compile(r"^(\d{1,2})\.$")
CLUSTER_TOL = 4.0   # 기준선 클러스터링 허용 오차(pt)
MATCH_TOL = 12.0    # 검출된 기준선에 번호를 붙일 때의 허용 오차(pt)
                    # — 일부 문항 번호는 10pt 가까이 들여쓰기가 어긋나 있다


def head_columns(doc):
    """문서 전체에서 문항 번호가 찍히는 x0 기준선들을 찾는다."""
    xs = []
    for page in doc:
        for w in page.get_text("words"):
            if NUM_RE.match(w[4]):
                xs.append(w[0])
    if not xs:
        return []
    xs.sort()
    clusters, cur = [], [xs[0]]
    for x in xs[1:]:
        if x - cur[-1] <= CLUSTER_TOL:
            cur.append(x)
        else:
            clusters.append(cur)
            cur = [x]
    clusters.append(cur)
    # 문항 번호 기준선이라면 문서 전체에 여러 번 반복해서 나타난다
    good = [sum(c) / len(c) for c in clusters if len(c) >= 3]
    return sorted(good)


def scan_pdf(path):
    doc = fitz.open(path)
    cols = head_columns(doc)
    if not cols:
        doc.close()
        return [], "번호 기준선 검출 실패(텍스트 레이어 없음 추정)"

    def col_of(x):
        best, bd = None, MATCH_TOL
        for i, cx in enumerate(cols):
            if abs(x - cx) <= bd:
                best, bd = i, abs(x - cx)
        return best

    def col_range(i):
        lo = cols[i] - 20
        hi = cols[i + 1] - 20 if i + 1 < len(cols) else 10 ** 6
        return lo, hi

    items = []
    expect = 1
    for pno in range(doc.page_count):
        page = doc[pno]
        words = page.get_text("words")
        heads = []
        for w in words:
            m = NUM_RE.match(w[4])
            if m and col_of(w[0]) is not None:
                heads.append((col_of(w[0]), w[1], int(m.group(1)), w))
        heads.sort(key=lambda h: (h[0], h[1]))
        accepted = []
        for h in heads:
            if h[2] == expect:
                accepted.append(h)
                expect += 1
        for idx, (ci, y0, no, w) in enumerate(accepted):
            lo, hi = col_range(ci)
            y_end = accepted[idx + 1][1] if idx + 1 < len(accepted) and accepted[idx + 1][0] == ci else 10 ** 6
            txt = [ww[4] for ww in words
                   if lo <= ww[0] < hi and y0 - 2 <= ww[1] < y_end]
            items.append({"no": no, "page": pno + 1, "text": " ".join(txt)})
    doc.close()
    return items, None


def parse_name(fn):
    m = re.match(r"(\d{4})년-(\d{2})월-(고[12])-(.+)-문제\.pdf$", fn)
    if m:
        return {"year": int(m.group(1)), "month": int(m.group(2)),
                "grade": "H1" if m.group(3) == "고1" else "H2", "subject": m.group(4)}
    return {"year": None, "month": None, "grade": None, "subject": fn[:-4]}


def main():
    out, problems = [], []
    files = sorted(f for f in os.listdir("inbox") if f.endswith(".pdf") and "해설" not in f)
    for fn in files:
        meta = parse_name(fn)
        items, err = scan_pdf(os.path.join("inbox", fn))
        if err or len(items) < 20:
            problems.append((fn, len(items), err or "문항 수 부족"))
        print(f"{fn}: {len(items)}문항" + (f"  <-- {err}" if err else ""))
        for it in items:
            out.append({"file": fn, **meta, "no": it["no"], "page": it["page"], "text": it["text"]})
    with open("scripts/all_items_text.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("\n총", len(out), "문항 -> scripts/all_items_text.json")
    if problems:
        print("\n[점검 필요]")
        for p in problems:
            print("  ", p)


main()
