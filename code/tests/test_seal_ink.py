# -*- coding: utf-8 -*-
"""大印下剔印泥（code/seal_ink.py；2026-11-10 从 open-guji-cv tests/test_dzg_layout.py 搬来）。"""
from __future__ import annotations


def test_seal_inkcut_removes_speckle_keeps_strokes():
    """大印下剔印泥：多孔碎点（印泥）抹白，实心笔画留下。"""
    import numpy as np
    from guji_book.shiji_wyg.seal_ink import inkcut
    rng = np.random.default_rng(0)
    img = np.full((300, 120), 255, np.uint8)
    dots = rng.random((300, 120)) < 0.25
    img[:150][dots[:150]] = 0                      # 上半：印泥碎点
    img[180:260, 50:62] = 0                        # 下半：一道实心竖笔
    img[60:120, 30:90] = 255
    img[80:92, 30:90] = 0                          # 印里一道实心横笔（印下的字）
    out = inkcut(img, (0, 300), 128)
    assert (out[180:260, 50:62] == 0).all()
    assert (out[80:92, 35:85] == 0).mean() > 0.9
    speck = (img[:60] == 0).sum()
    assert (out[:60] == 0).sum() < 0.1 * speck


def test_hooks_on():
    from guji_book.shiji_wyg import seal_ink
    assert seal_ink.GAP_SLOTS_EMPTY is True
