# -*- coding: utf-8 -*-
"""follow_ref_rival（k9）：同族异体不当对手，形近字照旧算。用 cv 的真关系层事实（`_RivalFacts`）。"""
from open_guji_cv.clustering.variants import VariantMap
from open_guji_cv.steps.seed_admit import _RivalFacts

import follow_ref_rival as m

F = _RivalFacts(VariantMap.load())


def _skip(ref, lib, cands, via="variants"):
    return m.rival_skip(ref=ref, lib=lib, cands=[(c, 0.9) for c in cands], via=via, facts=F)


def test_family_third_form_skipped():
    assert _skip("吳", "吴", ["吴", "呉", "昊"]) == ["呉"]       # 昊 形近、无边，仍算对手
    assert _skip("嵗", "歳", ["歳", "歲", "藏"]) == ["歲"]


def test_table_pairs_too():
    """嵗=歳、吳=吴 在册 yaml 的 follow_ref 表里，走表路（via=None）：k10 漏了这条，k11 补上。"""
    assert _skip("吳", "吴", ["吴", "呉", "昊"], via=None) == ["呉"]
    assert _skip("傳", "𫝊", ["𫝊", "博", "傅"], via=None) is None


def test_lookalikes_and_weak_edges_stay_rivals():
    assert _skip("傳", "𫝊", ["𫝊", "博", "傅"]) is None       # 傅：T2 单来源，不算同族
    assert _skip("教", "敎", ["敎", "赦", "敖"]) is None
    assert _skip("擊", "撃", ["撃", "繫", "摰"]) is None
