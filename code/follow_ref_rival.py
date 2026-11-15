"""follow_ref 领先差：同族异体不当对手（史記文淵閣本；k11 表路＋variants 路；k12 补「同族但边表缺边」）。

史記按整理本录字（`follow_ref_variants`）。三形家族的第三形（吴／呉／吳、嵗／歳／歲 里的第三个）贴得很近，被算成对手，
已判对的格卡在 `follow_ref_gap` 送审。本钩子只在算领先差时把这样的字排除；cov 门槛、领先门槛、硬疑问、diff 照旧。

一个候选字 c（不是 ref／lib）当「同族第三形」排除，要同时满足：
1. 表路（via=None）与 `follow_ref_variants` 路（via="variants"）都生效；
2. c 与整理本字、与配对形 lib 两头都「同族」，且至少一头是**强关系**，另一头至少同义：
   - 强关系＝同义＋（边表 T1，或 T2 且 `n_bridge ≥ 2`，或两字同在一个已审定的 `variant` 字组）；
   - 同义＝`facts.same_semantic`；
   - 两头都不在 never_group、edge_pair_exclude，且不同属某个 `near_form` 字组。
   k11 要求两头都是边表强关系；k12 放宽为「一头强、一头同义」，并把 variant 字组算作强关系，补上隐=𨼆（隠）、隐／隠（𨼆）、虗／虛（虚）
   这类边表缺边的同族。T2 单来源（傳／傅 twedu 一家、悦／恱 hydzd 一家）不算强，也不同义，照旧当对手。
形近字（昊／吴、傅／傳、敖／教、繫摰／擊撃）没有这样的关系，照旧算对手。

回放（r58 66 格＋r62 90 格）：66 格结果不变（30 格翻放行，两路盲读 0 错）；90 格新增 5 格（隐=𨼆 对手隠 3、隐隠 对手𨼆 1、虗虛 对手虚 1），
5 格字块图两路盲读 0 错。评估见 ai-team domain/CV/质检/领先差排除同族异体评估-2026-11-13/。

k13（A24 r68 评估 11-15）：新增钩子 `variant_norm`（cv #1554，seed_admit lane_variant_guard）。本书 codepoints 已把要放的字与候选异体归一
（canon 相同）时放 canon(字)；库首位是该字的**形近不同字**（明眀↔朋崩萌、凡凢↔几兄、揚↔楊、邊邉↔遏退、關闗関↔閱閻）时不放。
回放 71 格（witness3／coord_fallback 因 cand_variant 被拦、两形已归一）：56 格放、15 格不放，与 A24 两路盲读一致。
"""
from __future__ import annotations


def _grouped(f) -> bool:
    return any(kind == "variant" for _gid, kind in f.groups)


def _ok(f) -> bool:
    return not f.never and not f.edge_excluded and not any(kind == "near_form" for _gid, kind in f.groups)


def _strong(f, need_semantic: bool) -> bool:
    if not _ok(f):
        return False
    edge = bool(f.is_variant and (f.tier == "T1" or (f.tier == "T2" and f.n_bridge >= 2)))
    if edge and (f.same_semantic or not need_semantic):
        return True
    return bool(f.same_semantic and _grouped(f))


def _linked(strong_side: bool, f) -> bool:
    return strong_side or (f.same_semantic and _ok(f))


def rival_skip(*, ref, lib, cands, via, facts):
    out = []
    for c, _cov in cands:
        if c in (ref, lib) or c in out:
            continue
        fr, fl = facts(ref, c), facts(lib, c)
        sr, sl = _strong(fr, True), _strong(fl, False)
        if (sr or sl) and _linked(sr, fr) and _linked(sl, fl):
            out.append(c)
    return out or None



#: 形近不同字清单（键＝要放的字及其 canon，值＝库首位是这些字时不放）。书仓维护，加一条先看图。
LOOKALIKE = {
    "明": {"朋", "崩", "萌"}, "眀": {"朋", "崩", "萌"},
    "凡": {"几", "兄"}, "凢": {"几", "兄"},
    "揚": {"楊"}, "扬": {"楊"},
    "邊": {"遏", "退"}, "邉": {"遏", "退"},
    "關": {"閱", "閻"}, "闗": {"閱", "閻"}, "関": {"閱", "閻"},
}


def variant_norm(*, lane, char, form, canon, lib):
    if canon is None or not char or not form:
        return None
    c = canon(char)
    if c != canon(form):
        return None
    bad = LOOKALIKE.get(char, set()) | LOOKALIKE.get(c, set())
    if lib and lib in bad:
        return None
    return c
