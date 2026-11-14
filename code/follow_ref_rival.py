"""follow_ref 领先差：同族异体不当对手（史記文淵閣本，k9；SJ 请求、A24 定规则，2026-11-13；钩子 cv#1517）。

史記按整理本录字（`follow_ref_variants`）。三形家族的第三形（吴／呉／吳、嵗／歳／歲 里的第三个）贴得很近，被算成对手，
已判对的格卡在 `follow_ref_gap` 送审。本钩子只在算领先差时把这样的字排除；cov 门槛、领先门槛、硬疑问、diff 照旧。

一个候选字 c（不是 ref／lib）当「同族第三形」排除，要同时满足：
1. 表路（`follow_ref` 表里的对子，via=None）与 `follow_ref_variants` 路（via="variants"）都生效。k10 只认 variants 路，漏了：
   嵗=歳、吳=吴 都在册 yaml 的表里，走表路，k10 钩子被跳过、30 格一格没翻（r60，SJ-batch 发现）；
2. 与整理本字同义（`facts(ref, c).same_semantic`），且与配对形 lib 也有强异体边（族要自洽；lib 一侧不要求同义，吴／呉 在 vmap 里不同义但边是 T2 两来源）；
3. 关系层强异体：T1，或 T2 且 `n_bridge ≥ 2`（T2 单来源，如 傳／傅（twedu 一家），不算）；
4. 不在 never_group、edge_pair_exclude，且 ref／lib 与 c 不同属某个 `near_form` 字组。
形近字（昊／吴、傅／傳、敖／教、繫摰／擊撃）没有这样的边，照旧算对手。

66 格回放（r58 ★main）：30 格翻成放行（吳吴 13、嵗歳 17），两路盲读 0 错放。评估见 ai-team
domain/CV/质检/领先差排除同族异体评估-2026-11-13/。
"""
from __future__ import annotations


def _strong(f, need_semantic: bool) -> bool:
    return bool(f.is_variant and (f.same_semantic or not need_semantic) and not f.never and not f.edge_excluded
                and (f.tier == "T1" or (f.tier == "T2" and f.n_bridge >= 2))
                and not any(kind == "near_form" for _gid, kind in f.groups))


def rival_skip(*, ref, lib, cands, via, facts):
    out = []
    for c, _cov in cands:
        if c in (ref, lib) or c in out:
            continue
        if _strong(facts(ref, c), True) and _strong(facts(lib, c), False):
            out.append(c)
    return out or None
