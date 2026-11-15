# -*- coding: utf-8 -*-
"""follow_ref_rival（k12）：同族异体不当对手，形近字照旧算。用 cv 的真关系层事实（`_RivalFacts`）。"""
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
    """嵗=歳、吳=吴 在册 yaml 的 follow_ref 表里，走表路（via=None）。"""
    assert _skip("吳", "吴", ["吴", "呉", "昊"], via=None) == ["呉"]
    assert _skip("傳", "𫝊", ["𫝊", "博", "傅"], via=None) is None


def test_family_without_edge_k12():
    """k12：边表缺边但同义、且一头强关系的同族（r62）。"""
    assert _skip("隐", "𨼆", ["𨼆", "隠", "隱"], via=None) == ["隠", "隱"]
    assert _skip("隐", "隠", ["隠", "𨼆"], via=None) == ["𨼆"]
    assert _skip("虗", "虛", ["虛", "虚", "䖍"], via=None) == ["虚"]


def test_lookalikes_and_weak_edges_stay_rivals():
    assert _skip("傳", "𫝊", ["𫝊", "博", "傅"]) is None       # 傅：T2 单来源，不算同族
    assert _skip("教", "敎", ["敎", "赦", "敖"]) is None
    assert _skip("擊", "撃", ["撃", "繫", "摰"]) is None
    assert _skip("悦", "悅", ["悅", "恱"]) is None            # 恱：T2 单来源、不同义
    assert _skip("隐", "隠", ["隠", "聰"]) is None


def test_variant_norm_k13():
    """k13：两形已归一放 canon；库首位是形近不同字不放。"""
    canon = {"眀": "明", "凢": "凡"}.get
    f = lambda c: canon(c, c)
    assert m.variant_norm(lane="witness3", char="眀", form="明", canon=f, lib="明") == "明"
    assert m.variant_norm(lane="witness3", char="眀", form="明", canon=f, lib="朋") is None
    assert m.variant_norm(lane="witness3", char="凡", form="凢", canon=f, lib="几") is None
    assert m.variant_norm(lane="witness3", char="凡", form="凢", canon=f, lib="凡") == "凡"
    assert m.variant_norm(lane="witness3", char="嵗", form="歲", canon=f, lib="歲") is None   # 本表没归一
    assert m.variant_norm(lane="witness3", char="眀", form="明", canon=None, lib="明") is None
