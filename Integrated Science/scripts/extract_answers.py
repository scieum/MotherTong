# -*- coding: utf-8 -*-
"""해설 PDF의 정답표에서 문항별 정답을 뽑는다.

선택과목 해설 PDF 한 권에 4개 과목 정답표가 모두 들어 있으므로
'<과목명> 정답' 머리글로 해당 과목 구간을 먼저 찾은 뒤 파싱한다.
"""
import json
import os
import re
import sys

import fitz

CIRCLED = {"①": 1, "②": 2, "③": 3, "④": 4, "⑤": 5}
SUBJ_HEAD = {"물리학1": "물리학Ⅰ", "화학1": "화학Ⅰ", "생명과학1": "생명과학Ⅰ",
             "지구과학1": "지구과학Ⅰ", "통합과학": "통합과학"}


# 2022년 3월 해설 PDF는 원문자 ①~⑤를 유니코드 한자 영역의 사설 글리프로 찍는다.
# (화학Ⅰ·생명과학Ⅰ 정답표 이미지를 직접 대조해 확인한 대응)
GLYPH = {chr(0x6abe + i): chr(0x2460 + i) for i in range(5)}  # 0x6abe~0x6ac2 -> (1)~(5), 순서대로 대응


def normalize(text):
    for g, c in GLYPH.items():
        text = text.replace(g, c)
    return text


# 정답표 머리글은 '통합과학 정 답', '[통합과학]', '화학棯정답' 등 판본마다 제각각이라
# 머리글 대신 '1 ① 2 ② 3 ③' 형태의 정답 나열 자체를 찾는다.
RUN_START = re.compile(r"1\s*([①-⑤])\s*2\s*([①-⑤])\s*3\s*([①-⑤])")


def answers_for(sol_path, subject):
    doc = fitz.open(sol_path)
    text = normalize(" ".join(" ".join(p.get_text().split()) for p in doc))
    doc.close()
    if len(text) < 50:
        return None, "해설 PDF에 텍스트 레이어 없음(이미지 스캔)"

    runs = [m.start() for m in RUN_START.finditer(text)]
    if not runs:
        return None, "정답 나열을 찾지 못함(사설 글리프 등)"

    head = SUBJ_HEAD.get(subject, subject)
    start = None
    if len(runs) == 1:
        start = runs[0]
    else:
        # 선택과목 해설 한 권에 4개 과목 정답표가 함께 들어 있다.
        # 각 나열 바로 앞에 적힌 과목명으로 구간을 고른다.
        base = head.rstrip("Ⅰ")
        for r in runs:
            if base in text[max(0, r - 40):r]:
                start = r
                break
        if start is None:
            return None, f"'{head}' 구간을 특정하지 못함(정답 나열 {len(runs)}개)"

    out, expect = {}, 1
    for num, circ in re.findall(r"(\d{1,2})\s*([①-⑤])", text[start:start + 900]):
        if int(num) != expect:
            break
        out[expect] = CIRCLED[circ]
        expect += 1
    if len(out) < 20:
        return out, f"{len(out)}개만 파싱됨"
    return out, None


def main():
    result, problems = {}, []
    for fn in sorted(os.listdir("inbox")):
        if not fn.endswith("-문제.pdf"):
            continue
        sol = fn.replace("-문제.pdf", "-해설.pdf")
        stem = fn[:-len("-문제.pdf")]
        subject = stem.split("-")[-1]
        if not os.path.exists(os.path.join("inbox", sol)):
            problems.append((stem, "해설 PDF 없음"))
            continue
        ans, err = answers_for(os.path.join("inbox", sol), subject)
        if err:
            problems.append((stem, err))
        if ans:
            result[stem] = ans
    json.dump(result, open("scripts/answer_keys.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(len(result), "개 시험지 정답표 -> scripts/answer_keys.json")
    if problems:
        print("\n[정답 확보 실패]")
        for p in problems:
            print("  ", p[0], "—", p[1])


main()
