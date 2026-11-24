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
    # k27（v0.2，11-20）：71 对异体类里「图确为整理本字、库首位是另一个形近字」的 11 对，库首位是这些字时不放，维持送审
    "曠": {"壙"}, "齡": {"軨"}, "擔": {"檐"}, "祖": {"徂"}, "悦": {"税"}, "惟": {"帷"},
    "塼": {"摶"}, "矯": {"撟"}, "穰": {"禳"}, "蓋": {"盍"}, "渚": {"陼"},
}

#: 放刻形（k17 起）：整理本字 → 允许的刻形异体。库里该异体排在整理本字前才放、放刻形，否则送审。
#: k27 加 卷→巻（27:110:1:4、37:176:1:4、40:102:1:4 图为巻）、彊→疆（37:110:8:4 图为疆）。
RANK_PAIRS = {"圖": {"圗"}, "冀": {"兾"}, "凡": {"凢"}, "來": {"来"}, "卷": {"巻"}, "彊": {"疆"}}
#: 来/來 的库分只差 ≤0.01、名次是噪声（k23，A24 11-17）：写 来 须来分 ≥ 來分 + MARGIN_LAI。
MARGIN_LAI = 0.02

#: 取消码位归一后（v0.2 codepoints 取消 23 条）lane 通道放整理本变体（刻形）。变体 → 目标字。A24 11-20。
KEEP_CUR = {
    "眀": "明", "䏻": "能", "邉": "邊", "乆": "久", "椘": "楚", "戶": "户", "賛": "贊", "莭": "節", "噐": "器", "䜛": "讒",
    "廹": "迫", "眞": "真", "耻": "恥", "宼": "寇", "㓂": "寇", "靁": "雷", "挟": "挾", "冝": "宜", "㪚": "散", "甪": "角",
    "仟": "阡", "旍": "旌", "𡙇": "缺",
}


def _keep_cur(char, cur, lib, forms=()):
    # 方向二（37:225:5:9）：放行字 char 本身就是整理本变体（莭），cur 是库首位（卽），目标字（節）只在 forms 里 → 放 char（刻形）
    if char in KEEP_CUR and any(f == KEEP_CUR[char] for _, f, _ in forms):
        if lib and lib in LOOKALIKE.get(char, set()) | LOOKALIKE.get(KEEP_CUR[char], set()):
            return None
        return char
    # 方向一：cur（整理本字）是变体、char 是它的目标字 → 放 cur
    if cur and KEEP_CUR.get(cur) == char and cur != char:
        if lib and lib in LOOKALIKE.get(cur, set()) | LOOKALIKE.get(char, set()):
            return None
        return cur
    return None


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


# variant_rank（k17，11-16；k27 扩 RANK_PAIRS、加 来/來 margin 与 keep_cur，见上面表与函数）：Sheldon 11-15 定 圗兾凢来 不并码位、改流水线放行；11-16 定文字层照刻形写。
# 要 cv 带 #1573（v0.7.43）。A22 刻形版：库里异体排在参校本字之前才放、放刻形 form；否则送审。
# 取代 variant_rank_patch.py（Sheldon 11-16：圗兾凢来 文字层照刻形写）。A22 核过 cv 侧：返回 form 时 same(form, char) 成立（两形本就是 variants 异体对），
# cv 放行字＝form，证据 lane.variant_rank=hook、variant_from、variant_ranks 照记。

def variant_rank(*, lane, char, forms, cur, cands, lib):
    """放刻形 form：只在库里这个异体排在参校本字 char 前面（或 char 不在库前几名）时放；否则送审，不猜。"""
    r0 = _keep_cur(char, cur, lib, forms)
    if r0 is not None:
        return r0
    ok = RANK_PAIRS.get(char, set())
    hits = [(r, f) for r, f, _ in forms if r >= 1 and f in ok]      # 只看库名次；现字（名次 0）不算证据
    if not hits:
        return None
    r, f = min(hits)                                                 # 排最前的那个异体
    sc = {c: v for c, v in cands}
    if char == "來":                                                 # 只对 来/來 加 margin（k23）
        if char not in sc or f not in sc or sc[f] < sc[char] + MARGIN_LAI:
            return None
    else:
        r_char = next((i for i, (c, _) in enumerate(cands, 1) if c == char), None)
        if r_char is not None and r_char < r:
            return None                                              # 库认参校本字比认刻形更像：别写异体
    if lib and lib in LOOKALIKE.get(char, set()):
        return None
    return f
