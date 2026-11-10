"""大印压列时的印泥处理（史記文淵閣本，写本；2026-11-03 第 5 轮）。

原 cv `steps/row_segment.py` 的 `_seal_inkcut`＋书级开关 `seal_gap_slots_empty`、`seal_inkcut`，2026-11-10 搬进本书
（A20，cv「先搬自成一块的」）：本模块覆盖 cv `impl/keben/seal_ink`（code.yaml）就生效，算法未动。

- `GAP_SLOTS_EMPTY`（原 `seal_gap_slots_empty`）：卷首叶题署行（「漢　　太　　史　　令司馬遷　撰」「宋中郎外兵曹　參　軍裴　駰集解」）
  字距拉开，表里是跳着的格位；「文淵閣寶」大印压在这些空格位上，缺省只记空列端的表空格，中间的空格位里的印泥被切成字，
  格数对不上整理本、整列对位落空（01–10 册 p2 约 97 格）。开着时表首字与末字之间、表说空的格位落在印框里也记空。
- `inkcut`（原 `seal_inkcut`）：大印压着的列，先把印框行段里的印泥从列图里抹掉（印泥在二值图里是多孔碎点，开运算剩不下；
  刻字笔画实心留得下），再按平常的候选格网打分挑格，不再硬取等距格网。题署行字大、字距随手拉开，等距格网劈字、并字、
  印泥空格成假格（01–10 册 p2 约 80 格）。只改切分用的列图，Step4 裁字仍用原列图。
"""
from __future__ import annotations

GAP_SLOTS_EMPTY = True

#: 开运算核（像素）与开运算后保留的最小连通块（像素）。印泥在二值图里是多孔的碎点，开运算剩不下；
#: 刻字笔画实心，开运算后留下骨干，再在原墨里膨胀回去
SEAL_OPEN_K, SEAL_OPEN_MIN_AREA = 7, 150
#: 表里有雙行小注的列：小字笔画细，核换小的，不然小字跟印泥一起被抹掉（史記 03 p2 第 8 列）
SEAL_OPEN_K_NOTES, SEAL_OPEN_MIN_AREA_NOTES = 5, 60


def inkcut(img, rows: tuple[int, int], ink_threshold: int, notes: bool = False):
    """把列图 `rows` 行段里的印泥抹白：开运算（SEAL_OPEN_K）去掉多孔碎点，丢掉小块，剩下的笔画骨干在原墨里膨胀回去。"""
    import cv2
    import numpy as np
    a, b = rows
    g = img if img.ndim == 2 else img.mean(axis=2).astype(img.dtype)
    out = g.copy()
    ink = (g[a:b] < ink_threshold).astype(np.uint8)
    kk, min_area = (SEAL_OPEN_K_NOTES, SEAL_OPEN_MIN_AREA_NOTES) if notes else (SEAL_OPEN_K, SEAL_OPEN_MIN_AREA)
    k = np.ones((kk, kk), np.uint8)
    op = cv2.morphologyEx(ink, cv2.MORPH_OPEN, k)
    n, lab, st, _c = cv2.connectedComponentsWithStats(op, connectivity=8)
    small = st[:, cv2.CC_STAT_AREA] < min_area
    small[0] = False
    op[small[lab]] = 0
    keep = (cv2.dilate(op, k) > 0) & (ink > 0)
    band = out[a:b]
    band[(ink > 0) & ~keep] = 255
    return out
