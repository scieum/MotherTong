# -*- coding: utf-8 -*-
"""
문항 이미지 크롭 + 원본 번호/배점 마스킹 + 새 번호/배점 오버레이 엔진.
poppler 없이 PyMuPDF(fitz)만으로 렌더링한다.
"""
import fitz
import re
from PIL import Image, ImageDraw, ImageFont

ZOOM = 3.0  # 렌더링 배율 (고해상도)
FONT_BOLD = "C:/Windows/Fonts/malgunbd.ttf"


def _trim_trailing_whitespace(img, min_keep_ratio=0.35, pad=25):
    """이미지 하단의 빈 여백(쪽번호 제외 후 남는 공백)을 잘라낸다."""
    import numpy as np

    gray = img.convert("L")
    arr = np.array(gray)
    # 단 사이 구분선(세로줄 1~2px)이 크롭에 들어오면 모든 행에 잉크가 있는 것으로
    # 잡혀 여백이 전혀 잘리지 않는다. 행마다 어두운 픽셀이 일정 개수를 넘을 때만
    # 내용이 있는 행으로 본다.
    min_ink = max(4, int(arr.shape[1] * 0.004))
    row_has_ink = (arr < 235).sum(axis=1) > min_ink
    ink_rows = np.where(row_has_ink)[0]
    if len(ink_rows) == 0:
        return img
    last_ink = int(ink_rows[-1])
    new_h = min(img.height, last_ink + pad)
    new_h = max(new_h, int(img.height * min_keep_ratio))
    if new_h >= img.height:
        return img
    return img.crop((0, 0, img.width, new_h))


def _percentile(vals, p):
    s = sorted(vals)
    k = int(len(s) * p)
    k = min(max(k, 0), len(s) - 1)
    return s[k]


def _robust_edge_max(vals, gap_threshold=25):
    """가장 바깥쪽부터 훑어 내려가며, 본문과 큰 간격(gap_threshold)으로 뚝 떨어진
    가장자리 장식 요소(세로 탭 등)를 잘라내고 실제 본문의 최대값을 반환한다."""
    xs = sorted(vals)
    if len(xs) < 2:
        return xs[0] if xs else 0
    for i in range(len(xs) - 1, 0, -1):
        if xs[i] - xs[i - 1] > gap_threshold:
            return xs[i - 1]
    return xs[-1]


def find_column_divider(page):
    """페이지 중앙 부근에서 단어 x0 값의 가장 큰 간격을 찾아 실제 컬럼 경계로 쓴다.
    (좌우 컬럼 폭이 정확히 절반씩이 아닌 문서가 있어 기하학적 중앙값은 신뢰할 수 없다.)"""
    words = page.get_text("words")
    pw = page.rect.width
    x0s = sorted(set(round(w[0], 1) for w in words))
    lo, hi = pw * 0.25, pw * 0.78
    best_gap, divider = 0, pw / 2
    for a, b in zip(x0s, x0s[1:]):
        if (lo <= a <= hi or lo <= b <= hi) and (b - a) > best_gap:
            best_gap, divider = b - a, (a + b) / 2
    if best_gap < 15:
        return pw / 2
    return divider


def detect_columns(page):
    pw = page.rect.width
    words = page.get_text("words")
    mid = find_column_divider(page)
    left = [w for w in words if w[0] < mid]
    right = [w for w in words if w[0] >= mid]
    lx0 = _percentile([w[0] for w in left], 0.01) if left else 40
    lx1 = _robust_edge_max([w[2] for w in left]) if left else mid - 10
    rx0 = _percentile([w[0] for w in right], 0.01) if right else mid + 10
    rx1 = _robust_edge_max([w[2] for w in right]) if right else pw - 40
    # 중앙선이 왼쪽 단의 본문 글자 안쪽으로 들어와 있는 판본이 있어(글자 끝 413.3,
    # 중앙선 412.9) 중앙선으로만 자르면 오른쪽 끝 글자가 날아간다.
    # 왼쪽 단의 글자 끝이 오른쪽 단의 글자 시작보다 앞서면 그 사이를 경계로 쓰고,
    # 그렇지 않으면(중앙선 검출이 틀려 좌우가 섞인 경우) 중앙선 기준으로 되돌린다.
    if lx1 < rx0:
        lx1 = min(lx1 + 15, rx0 - 2)
        rx0 = max(rx0 - 15, lx1 + 2)
    else:
        lx1, rx0 = mid - 4, mid + 4
    return {"L": (lx0 - 15, lx1), "R": (rx0, rx1 + 15)}


def find_number_word(page, num):
    target = f"{num}."
    words = page.get_text("words")
    cands = [w for w in words if w[4] == target and w[6] == 0]
    cands.sort(key=lambda w: w[1])
    return cands[0] if cands else None


SCORE_RE = re.compile(r"^\[?(\d(\.\d)?)점\]?$")
PAGE_NUM_RE = re.compile(r"^\d{1,3}$")


def find_page_number_cutoff(page, x_range=None):
    """페이지 하단 영역에 있는 쪽번호 워드의 y0을 반환.

    x_range를 주면 해당 단의 가로 범위 안 워드만 후보로 쓴다 —
    다른 단 내용 속 숫자를 쪽번호로 오인하는 것을 막는다.
    쪽번호는 그 줄에 홀로 있으므로, 같은 줄에 다른 글자가 있으면 후보에서 뺀다
    ('ㄴ. 25 ℃에서 ...' 같은 본문 줄의 숫자를 쪽번호로 잡는 오류를 막는다).
    """
    ph = page.rect.height
    words = page.get_text("words")
    if x_range is not None:
        words = [w for w in words if x_range[0] - 20 <= w[0] <= x_range[1] + 20]

    def alone_on_line(w):
        return not any(abs(x[1] - w[1]) < 4 and x is not w and not PAGE_NUM_RE.match(x[4])
                       for x in words)

    cands = [w for w in words
             if w[1] > ph * 0.85 and PAGE_NUM_RE.match(w[4]) and alone_on_line(w)]
    cands += [w for w in words if w[1] > ph * 0.8 and "확인" in w[4]]
    if not cands:
        return None
    return min(w[1] for w in cands)


def find_score_word(page, x_range, y0, y1):
    words = page.get_text("words")
    best = None
    for w in words:
        if not (x_range[0] - 20 <= w[0] <= x_range[1] + 20):
            continue
        if not (y0 - 5 <= w[1] <= y1 + 5):
            continue
        txt = w[4]
        if "점" in txt and ("[" in txt or "]" in txt or SCORE_RE.match(txt)):
            if best is None or w[1] < best[1]:
                best = w
    return best


def locate_item(doc, orig_no):
    """orig_no가 있는 페이지, 번호 워드, 다음 번호 워드(있다면)를 찾는다."""
    for pno in range(doc.page_count):
        page = doc[pno]
        w = find_number_word(page, orig_no)
        if w:
            w_next = find_number_word(page, orig_no + 1)
            return pno, page, w, w_next
    return None, None, None, None


def crop_item(pdf_path, orig_no, new_no, new_score_label, out_path, keep_score=False):
    """문항 하나를 잘라 PNG로 저장한다.

    keep_score=True면 원본 배점 표기를 그대로 두고 번호만 새로 붙인다
    (주제별 문항 모음처럼 배점을 재배정하지 않는 산출물용).
    문항이 단이나 페이지를 넘어가면 각 조각을 잘라 세로로 이어 붙인다.
    """
    doc = fitz.open(pdf_path)
    pno, page, w, _ = locate_item(doc, orig_no)
    if w is None:
        doc.close()
        return False, f"item {orig_no} not found in {pdf_path}"

    segs, wnext = item_segments(doc, pno, w, orig_no)
    if not segs:
        doc.close()
        return False, f"item {orig_no}: 구간을 잡지 못함"

    mat = fitz.Matrix(ZOOM, ZOOM)
    parts, clips = [], []
    for i, (p, col, y0, y1) in enumerate(segs):
        pg = doc[p]
        cx0, cx1 = _slot_x_range(pg, col)
        clip = fitz.Rect(cx0, y0, cx1, y1)

        # 선택지(1~5) 행이 하단 경계에 걸리면 경계를 그 아래로 확장한다.
        # (촘촘한 조판에서 다음 문항 번호와 선택지 행이 몇 pt 겹치는 원본이 있다)
        if i == len(segs) - 1:
            circ = [x for x in pg.get_text("words")
                    if any(c in x[4] for c in "①②③④⑤")
                    and cx0 - 20 <= x[0] <= cx1 + 20
                    and y0 < x[1] < y1 + 8 and x[3] > y1]
            if circ:
                clip.y1 = max(x[3] for x in circ) + 3

        pix = pg.get_pixmap(clip=clip, matrix=mat, alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        if i == len(segs) - 1:
            img = _trim_trailing_whitespace(img, min_keep_ratio=0.1 if len(segs) > 1 else 0.35)
        parts.append(img)
        clips.append(clip)

    if len(parts) == 1:
        img = parts[0]
    else:
        width = max(p.width for p in parts)
        gap = int(ZOOM * 4)
        img = Image.new("RGB", (width, sum(p.height for p in parts) + gap * (len(parts) - 1)),
                        "white")
        y = 0
        for i, p in enumerate(parts):
            img.paste(p, (0, y))
            y += p.height + gap

    draw = ImageDraw.Draw(img)
    clip0 = clips[0]

    def to_local(rect):
        return ((rect[0] - clip0.x0) * ZOOM, (rect[1] - clip0.y0) * ZOOM,
                (rect[2] - clip0.x0) * ZOOM, (rect[3] - clip0.y0) * ZOOM)

    # 원본 번호 마스킹 + 새 번호 오버레이
    pad = 3 * ZOOM
    nx0, ny0, nx1, ny1 = to_local(w[:4])
    # 번호가 단 왼쪽 끝에 붙어 있으면 그리는 위치가 캔버스 밖으로 나가 앞자리가 잘린다
    mx0 = max(nx0 - pad, 1)
    draw.rectangle([mx0, ny0 - pad, nx1 + pad, ny1 + pad], fill="white")
    font = ImageFont.truetype(FONT_BOLD, int((ny1 - ny0) * 0.95))
    draw.text((mx0, ny0 - pad * 0.4), f"{new_no}.", fill="black", font=font)

    # 원본 배점 마스킹 (있으면)
    sw = None if keep_score else find_score_word(
        doc[segs[0][0]], (clip0.x0, clip0.x1), w[1], clips[0].y1)
    score_badge_needed = False
    if sw is not None:
        sx0, sy0, sx1, sy1 = to_local(sw[:4])
        draw.rectangle([sx0 - pad, sy0 - pad, sx1 + pad, sy1 + pad], fill="white")
        sfont = ImageFont.truetype(FONT_BOLD, int((sy1 - sy0) * 0.95))
        draw.text((sx0 - pad, sy0 - pad * 0.4), f"[{new_score_label}]", fill="black", font=sfont)
    elif not keep_score:
        # 원본에 배점 표기가 없던 문항(무마크 2점) -> 새 배점을 우상단 배지로 표시
        score_badge_needed = True
        badge_text = f"[{new_score_label}]"
        bfont = ImageFont.truetype(FONT_BOLD, max(int(img.height * 0.035), 20))
        bbox = draw.textbbox((0, 0), badge_text, font=bfont)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        bx1, by0 = img.width - 10, 8
        draw.rectangle([bx1 - tw - 12, by0 - 4, bx1 + 4, by0 + th + 8],
                       outline="black", width=2, fill="white")
        draw.text((bx1 - tw - 6, by0), badge_text, fill="black", font=bfont)

    img.save(out_path)
    doc.close()
    return True, {"score_badge_needed": score_badge_needed,
                  "segments": [(p + 1, c) for p, c, _, _ in segs]}


# ---------------------------------------------------------------------------
# 컬럼/페이지를 넘어가는 문항 처리
#
# 2단 조판에서 문항이 왼쪽 단 하단에서 시작해 오른쪽 단 상단으로 이어지거나,
# 페이지를 넘어가는 경우가 있다. crop_item은 시작 지점이 속한 단만 잘라내므로
# 이런 문항은 뒷부분(<보기>·선택지)이 통째로 잘려 나간다.
# 아래 함수는 문항이 차지하는 단들을 순서대로 잘라 세로로 이어 붙인다.
# ---------------------------------------------------------------------------

HEAD_BAND = 0.12           # 페이지 상단 이 비율까지는 머리글 영역으로 본다
MIN_CONTINUATION_WORDS = 10 # 이어지는 단에 이만큼은 본문 워드가 있어야 이어진 것으로 인정
CONTINUES_GAP = 30       # 단 바닥에서 이만큼 위에서 내용이 끝나면 다음 단으로 안 넘어간 것


def _slot_x_range(page, col):
    return detect_columns(page)[col]


def _slot_top(page, x_range):
    """해당 단에서 본문이 시작되는 y (머리글·쪽번호 제외)."""
    ph = page.rect.height
    ys = [w[1] for w in page.get_text("words")
          if x_range[0] - 5 <= w[0] <= x_range[1] + 5 and ph * 0.04 < w[1] < ph * 0.9]
    return min(ys) if ys else ph * 0.09


def _slot_bottom(page, x_range):
    bottom = page.rect.height * 0.92
    pn_y = find_page_number_cutoff(page, x_range)
    if pn_y is not None:
        bottom = min(bottom, pn_y - 10)
    return bottom


def _col_of(page, x):
    return "L" if x < find_column_divider(page) else "R"


def find_next_number(doc, pno, orig_no):
    """다음 문항 번호를 현재 페이지부터 다음 페이지까지 찾는다."""
    for p in (pno, pno + 1):
        if p >= doc.page_count:
            break
        w = find_number_word(doc[p], orig_no + 1)
        if w is not None:
            return p, w
    return None, None


def _last_content_y(page, x_range, y0, y1):
    ys = [w[3] for w in page.get_text("words")
          if x_range[0] - 5 <= w[0] <= x_range[1] + 5 and y0 <= w[1] <= y1]
    return max(ys) if ys else y0


def item_segments(doc, pno, w, orig_no):
    """문항이 차지하는 (페이지, 단, y0, y1) 구간들을 순서대로 돌려준다.

    한 단 안에서 끝나는 보통의 문항은 구간이 하나다. 내용이 그 단 바닥까지
    이어질 때만 다음 단으로 넘어간 것으로 보고 구간을 더한다.
    """
    page = doc[pno]
    col = _col_of(page, w[0])
    npno, wnext = find_next_number(doc, pno, orig_no)

    # 다음 번호가 같은 페이지·같은 단에 있으면 한 구간으로 끝난다.
    if wnext is not None and npno == pno and _col_of(page, wnext[0]) == col:
        return [(pno, col, w[1] - 6, wnext[1] - 6)], wnext

    segs = []
    p, c, first = pno, col, True
    while True:
        pg = doc[p]
        xr = _slot_x_range(pg, c)
        y0 = w[1] - 6 if first else _slot_top(pg, xr)

        if wnext is not None and p == npno and c == _col_of(doc[npno], wnext[0]):
            # 다음 문항 번호 위에 '머리글이 아닌' 본문이 실제로 있을 때만 이어진 것으로 본다.
            # (단 맨 위의 '과학탐구 영역 / 화학Ⅰ / 쪽번호' 머리글을 문항 내용으로 오인하지 않기 위함)
            head_band = pg.rect.height * HEAD_BAND
            body = [x for x in pg.get_text("words")
                    if xr[0] - 5 <= x[0] <= xr[1] + 5
                    and head_band < x[1] < wnext[1] - 2]
            if len(body) >= MIN_CONTINUATION_WORDS:
                segs.append((p, c, min(x[1] for x in body) - 6, wnext[1] - 6))
            break

        bottom = _slot_bottom(pg, xr)
        if bottom - y0 > 5:
            segs.append((p, c, y0, bottom))
        # 내용이 단 바닥까지 닿지 않으면 문항은 이 단에서 끝난 것이다
        if _last_content_y(pg, xr, y0, bottom) < bottom - CONTINUES_GAP:
            break

        first = False
        if c == "L":
            c = "R"
        else:
            p, c = p + 1, "L"
        if p >= doc.page_count or p > pno + 1:
            break
    return segs, wnext
