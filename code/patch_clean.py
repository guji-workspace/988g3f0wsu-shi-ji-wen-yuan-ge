"""发前清格（史記文淵閣本，写本；2026-11-10 SJ「切分快筛」装饰类）。

覆盖 cv `impl/keben/patch_clean`（code.yaml）。格框、格号都不动，出字块前把不属于本格的墨抹白：

1. **邻格残笔**：整列列图先剥掉长直线（界行竖线、版框横线，不剥的话写本连笔加界行把一串字连成一块），再分连通块，
   每块墨归「框内像素最多」的那一格。主体在别格、伸进本框的部分又不到本框墨 `FRINGE_MAX`（35%）的「边角块」抹白。
   伸进来的部分超过 35%、或伸进框里超过框高 30% 的是笔画相连的两个字，不动（那是切分层的事）。夹注同号另半不算（发前已按中缝抹白）。
2. **贴列边小块**：本格自己的、贴着列图左右边、不到本框墨 15% 的小块（邻列字或界行的残墨）抹白。
3. **长直线**：框里剥出的界行竖线抹白；版框横线只在列首、列尾格抹（列中整宽的横笔可能是字，例如「一」）。

保险：一格要抹的墨超过本格墨 `MAX_ERASE`（40%）就整格不清（多半是字本身被当成了线或别格的墨）。抹完按剩下的墨
收紧字块与 `bbox`（同 cv `_apply_seam`），重算 `ink_ratio`。

判据与 r35 十册的量法见 guji-manager doc/01-粗校/切分快筛.md；检测工具 `shiji/seg-detect/tools/ctx2.py` 同一套墨账。
"""
from __future__ import annotations

#: 竖向开运算长度（像素）：剥界行。单字一笔到不了这么长。
VLINE_LEN = 200
#: 横向开运算长度占列宽：剥版框横线。
HLINE_FRAC = 0.85
#: 边角块：在本框里的部分 ≤ 本框墨这么多才算外来残笔。
FRINGE_MAX = 0.35
#: 边角块伸进本框的深度（从靠主人那一边的框边量起）不超过框高这么多。写本上下两字常常一笔相连（「抄」的撇连到下面
#: 「内」），连成一块的主体在下格，伸进本框的那截却是本字的一大笔：按深度挡住，只抹贴边的浅残笔。
FRINGE_DEPTH = 0.30
#: 贴列边小块：≤ 本框墨这么多。
SIDE_MAX = 0.15
#: 连通块小于这么多像素不计入本框墨（碎点）。
MIN_PX = 8
#: 一格抹掉的墨超过本格墨这么多就不清。
MAX_ERASE = 0.40
#: 收紧余量（同 extractor.TIGHT_MARGIN）。
TIGHT_MARGIN = 2


def _ink_ratio(gray):
    import cv2
    import numpy as np
    if gray.size == 0:
        return 0.0
    _, b = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return float(np.count_nonzero(b)) / b.size


def plan_column(img, pairs, ink_threshold: int = 128) -> dict:
    """每格要抹的像素（列图坐标的布尔掩码，只在格框范围内）：{pairs 下标: (mask, 原因计数)}。不改输入。"""
    import cv2
    import numpy as np
    g = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    H, W = g.shape[:2]
    ink = (g < ink_threshold).astype(np.uint8)
    vl = cv2.morphologyEx(ink, cv2.MORPH_OPEN, np.ones((VLINE_LEN, 1), np.uint8)) > 0
    hl = cv2.morphologyEx(ink, cv2.MORPH_OPEN, np.ones((1, max(40, int(HLINE_FRAC * W))), np.uint8)) > 0
    core = ((ink > 0) & ~vl & ~hl).astype(np.uint8)
    n, lab, st, _c = cv2.connectedComponentsWithStats(core, connectivity=8)
    area = st[:, cv2.CC_STAT_AREA]

    cells = []   # (pairs 下标, inst, (x0, y0, x1, y1))
    for k, (inst, patch) in enumerate(pairs):
        if patch is None or getattr(patch, "size", 0) == 0 or inst.cell_type != "char":
            continue
        x0, y0, x1, y1 = (int(round(v)) for v in inst.bbox)
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        if x1 > x0 and y1 > y0:
            cells.append((k, inst, (x0, y0, x1, y1)))
    if not cells:
        return {}
    comp_in: dict[int, dict[int, int]] = {}
    for j, (_k, _inst, (x0, y0, x1, y1)) in enumerate(cells):
        sub = lab[y0:y1, x0:x1]
        ids, cnt = np.unique(sub[sub > 0], return_counts=True)
        for i, c in zip(ids.tolist(), cnt.tolist()):
            comp_in.setdefault(i, {})[j] = c
    owner = {i: max(d.items(), key=lambda t: t[1])[0] for i, d in comp_in.items()}
    ys = [b[1] for _k, _i, b in cells]
    first_y, last_y = min(ys), max(b[3] for _k, _i, b in cells)

    out = {}
    for j, (k, inst, (x0, y0, x1, y1)) in enumerate(cells):
        pieces = [(i, d[j]) for i, d in comp_in.items() if j in d]
        box_ink = sum(c for i, c in pieces if area[i] >= MIN_PX)
        if box_ink <= 0:
            continue
        sl = lab[y0:y1, x0:x1]
        erase_ids = []
        why = {"fringe": 0, "side": 0, "vline": 0, "hline": 0}
        for i, c in pieces:
            o = owner[i]
            if o == j:
                x, _y, w, _h, a = st[i]
                if (x <= 1 or x + w >= W - 1) and c < SIDE_MAX * box_ink and a >= MIN_PX:
                    erase_ids.append(i)
                    why["side"] += c
                continue
            if c > FRINGE_MAX * box_ink:
                continue
            oi = cells[o][1]
            if oi.idx == inst.idx and (oi.sub or "") != (inst.sub or ""):
                continue                      # 夹注同号另半：发前已抹白
            yy = np.nonzero((sl == i).any(axis=1))[0]
            ob = cells[o][2]
            if (ob[1] + ob[3]) / 2 >= (y0 + y1) / 2:     # 主人在下：从框底往上量
                depth = (y1 - y0 - int(yy[0])) / (y1 - y0)
            else:                                         # 主人在上：从框顶往下量
                depth = (int(yy[-1]) + 1) / (y1 - y0)
            if depth > FRINGE_DEPTH:
                continue
            erase_ids.append(i)
            why["fringe"] += c
        m = np.isin(sl, erase_ids) if erase_ids else np.zeros(sl.shape, bool)
        v = vl[y0:y1, x0:x1]
        why["vline"] = int(v.sum())
        m |= v
        if y0 <= first_y + 1 or y1 >= last_y - 1:   # 列首、列尾格才抹版框横线
            h = hl[y0:y1, x0:x1]
            why["hline"] = int(h.sum())
            m |= h
        own = int((ink[y0:y1, x0:x1] > 0).sum())
        if not m.any() or own <= 0 or int(m.sum()) > MAX_ERASE * own:
            continue
        out[k] = (m, why)
    return out


def clean_column(img, pairs, ink_threshold: int = 128):
    """cv `cell_shrink` 发前清格钩子：按 `plan_column` 抹白并收紧字块与 bbox。"""
    import numpy as np
    plan = plan_column(img, pairs, ink_threshold)
    if not plan:
        return pairs
    out = list(pairs)
    for k, (m, _why) in plan.items():
        inst, patch = pairs[k]
        x0, y0, x1, y1 = (int(round(v)) for v in inst.bbox)
        if patch.shape[0] != y1 - y0 or patch.shape[1] != x1 - x0:
            continue                          # 字块与 bbox 对不上（不该有），不碰
        # m 是裁到列图范围内的；bbox 出了列图的那截（不该有）补 False
        full = np.zeros(patch.shape[:2], bool)
        cy0, cx0 = max(0, y0), max(0, x0)
        full[cy0 - y0:cy0 - y0 + m.shape[0], cx0 - x0:cx0 - x0 + m.shape[1]] = m
        p = patch.copy()
        p[full] = 255
        dark = p < ink_threshold
        rows = np.nonzero(dark.any(axis=1))[0]
        cols = np.nonzero(dark.any(axis=0))[0]
        if rows.size == 0 or cols.size == 0:
            continue                          # 抹空了：不清（保险，正常到不了）
        r0 = max(0, int(rows[0]) - TIGHT_MARGIN)
        r1 = min(p.shape[0], int(rows[-1]) + 1 + TIGHT_MARGIN)
        c0 = max(0, int(cols[0]) - TIGHT_MARGIN)
        c1 = min(p.shape[1], int(cols[-1]) + 1 + TIGHT_MARGIN)
        p = np.ascontiguousarray(p[r0:r1, c0:c1])
        bx0, by0 = inst.bbox[0], inst.bbox[1]
        inst.bbox = (float(bx0 + c0), float(by0 + r0), float(bx0 + c1), float(by0 + r1))
        inst.ink_ratio = round(_ink_ratio(p), 4)
        out[k] = (inst, p)
    return out
