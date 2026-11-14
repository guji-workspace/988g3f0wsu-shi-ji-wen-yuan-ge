# -*- coding: utf-8 -*-
"""史記（写本）职名页自己的实现 `books/shiji_wyg/roster_segment`：写本「臣」斜贴邻字的拆分，
以及 Step3 壳按册的套书选它（殿本册仍用殿本的）。合成数据，不读真书。"""

from __future__ import annotations

import open_guji_cv.steps  # noqa: F401  —— 注册 Step / 产物种类
from helpers import make_book, run_keben_chain
from guji_book.shiji_wyg import roster_segment as SJ
from test_roster_segment import W, _roster_column, _xieben_column


def test_shiji_splits_stuck_chen_by_page_chen_row():
    cols = [(_roster_column()[0], (10.0, W - 10.0)) for _ in range(2)]
    cols.append((_xieben_column(1620), (10.0, W - 10.0)))
    rc = SJ.segment_roster_page(cols)[2]
    assert len(rc.items) == 6 and rc.items[3].y0 == 1620


def _run(tmp_path, monkeypatch, **bk):
    book = make_book(expected_cols=4, chars_per_line=21, params={"row_segment": {"roster_pages": ["1"]}}, **bk)
    return run_keben_chain(tmp_path, monkeypatch, book=book, through="row_segment", h=2000,
                           n_cols=4, w=500, period=100, col_n_chars={4: 3, 3: 7, 2: 12, 1: 5})


def test_step_uses_shiji_module_only_for_shiji_books(tmp_path, monkeypatch):
    calls = []
    real = SJ.segment_roster_page
    monkeypatch.setattr(SJ, "segment_roster_page", lambda *a, **k: calls.append(1) or real(*a, **k))
    _run(tmp_path / "dian", monkeypatch, seg_set="siku_zongmu")
    assert not calls                                   # 显式写殿本的册走殿本的实现（本仓有 code/，不写 seg_set 就归本书）
    _run(tmp_path / "sj", monkeypatch, seg_set="shiji_wyg")
    assert calls                                       # 史記册走本仓 code/ 的


def test_header_cols_accepts_ref_variant_spellings():
    # 整理本把撰者行写成「集觧」「隼解」「索隐」「索𨼆」、卷题写成「巻」「史訖」时也要认作卷端标题列
    # （r50：25:16:4、25:44:4、29:106:5；r59：41:2:5、34:2:2、40:182:2）。k11 起按「史記卷N」锚点位置认，不靠正则补词
    from guji_book.shiji_wyg.roster_segment import header_cols
    for anchor in ("史記卷一", "史記巻九十五", "史訖卷一百二十七"):
        for zhuan in ("宋中郎外兵曹參軍裴駰集觧", "宋中郎外兵曹參軍裴駰隼解"):
            for suoyin in ("唐國子博士弘文館學士司馬貞索隐", "唐國子博士𢎞文館學士司馬貞索𨼆"):
                refs = {1: "欽定四庫全書", 2: anchor, 3: "漢太史令司馬遷撰", 4: zhuan, 5: suoyin,
                        6: "唐諸王侍讀率府長史張守節正義", 7: "五帝本紀第一", 8: "太史公曰余讀諜記黄帝以來皆有年數"}
                assert header_cols(refs) == {1, 2, 3, 4, 5, 6, 7}
    # 没有锚点的页不认（太史公自序正文「…作宋世家第八」曾被旧正则当题署，42:69:8）
    assert header_cols({1: "嘉微子問太師作宋世家第八", 2: "宋中郎外兵曹參軍裴駰集解"}) == set()
