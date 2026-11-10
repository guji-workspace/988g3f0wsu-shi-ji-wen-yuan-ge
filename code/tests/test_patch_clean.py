# -*- coding: utf-8 -*-
"""发前清格（code/patch_clean.py，2026-11-10 SJ）：抹邻格边角残笔、贴边小块、界行；笔画相连伸得深的不动；格数格序不变。"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class _Inst:
    idx: int
    bbox: tuple
    cell_type: str = "char"
    sub: str | None = None
    ink_ratio: float = 0.0


def _col():
    import numpy as np
    img = np.full((400, 120), 255, np.uint8)
    img[20:90, 30:90] = 0          # 第 1 格字身
    img[110:180, 30:90] = 0        # 第 2 格字身
    img[95:104, 40:44] = 0         # 第 2 格主体连着的一截残笔伸进第 1 格框底（浅）
    img[103:110, 40:44] = 0
    return img


def _pairs(img, boxes):
    return [(_Inst(i, b), img[int(b[1]):int(b[3]), int(b[0]):int(b[2])].copy()) for i, b in enumerate(boxes)]


def test_shallow_fringe_erased_and_box_tightened():
    from guji_book.shiji_wyg.patch_clean import clean_column
    img = _col()
    boxes = [(28.0, 18.0, 92.0, 106.0), (28.0, 106.0, 92.0, 182.0)]
    out = clean_column(img, _pairs(img, boxes))
    assert [o[0].idx for o in out] == [0, 1]
    inst, p = out[0]
    assert (p < 128).sum() == 70 * 60                 # 只剩字身
    assert inst.bbox[3] <= 92                          # 收紧到字身＋余量
    assert out[1][0].bbox == boxes[1]                  # 第 2 格不动


def test_deep_connected_stroke_kept():
    """「抄」的撇连到下面「内」：连成一块的主体在下格，但伸进本框很深，不抹。"""
    import numpy as np
    from guji_book.shiji_wyg.patch_clean import clean_column
    img = np.full((400, 120), 255, np.uint8)
    img[20:60, 30:60] = 0                              # 第 1 格左半字身
    img[110:180, 30:90] = 0                            # 第 2 格大字身
    img[45:110, 70:76] = 0                             # 一撇从第 1 格中部一路连到第 2 格
    boxes = [(28.0, 18.0, 92.0, 106.0), (28.0, 106.0, 92.0, 182.0)]
    out = clean_column(img, _pairs(img, boxes))
    assert out[0][0].bbox == boxes[0]


def test_vertical_rule_erased():
    from guji_book.shiji_wyg.patch_clean import clean_column
    img = _col()
    img[:, 100:102] = 0                                # 贯穿整列的界行
    boxes = [(28.0, 18.0, 104.0, 106.0), (28.0, 106.0, 92.0, 182.0)]
    out = clean_column(img, _pairs(img, boxes))
    inst, p = out[0]
    assert inst.bbox[2] <= 92 + 1                      # 界行抹掉后右边收回字身
