# -*- coding: utf-8 -*-
"""k24：题署／职名整列等分重切后切点挪到墨谷（`roster_segment.valley_snap`）。合成行墨量，不读真书。"""
from __future__ import annotations

import numpy as np

from guji_book.shiji_wyg import roster_segment as SJ


def test_cut_moves_to_white_gap():
    ink = np.full(300, 20, dtype=np.int64)
    ink[120:140] = 0                     # 字间白缝在 120–139，等分切点在 100（字腰）
    assert SJ.valley_snap(ink, [0, 100, 300]) == [0, 130, 300]


def test_small_gain_keeps_cut():
    ink = np.full(300, 20, dtype=np.int64)
    ink[110:115] = 18                    # 只比原位少 2 个墨点：不挪
    assert SJ.valley_snap(ink, [0, 100, 300]) == [0, 100, 300]


def test_cut_already_white_stays():
    ink = np.full(300, 20, dtype=np.int64)
    ink[90:140] = 0
    assert SJ.valley_snap(ink, [0, 100, 300]) == [0, 100, 300]


def test_order_kept_and_ends_fixed():
    ink = np.full(400, 30, dtype=np.int64)
    ink[150:152] = 0                     # 两条切点（100、200）都想去 150 附近：第二条不能越过第一条
    out = SJ.valley_snap(ink, [0, 133, 266, 400])
    assert out[0] == 0 and out[-1] == 400
    assert out[0] < out[1] < out[2] < out[3]
