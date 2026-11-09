# -*- coding: utf-8 -*-
"""本书书级代码的测试（2026-11-09 从 open-guji-cv tests/ 搬来）。

跑法：装好 open-guji-cv（可编辑安装，要用 cv 仓 tests/ 里的 helpers），在本仓根 `python -m pytest code/tests -q`。
本目录不进指纹（不是 code.yaml 覆盖的模块）；`guji code check` 不查这里的 import。
"""
import sys
from pathlib import Path

import open_guji_cv

CV_TESTS = Path(open_guji_cv.__file__).resolve().parents[1] / "tests"
if str(CV_TESTS) not in sys.path:
    sys.path.insert(0, str(CV_TESTS))       # cv 的 helpers（make_book、run_keben_chain…）

from open_guji_cv.core import book_code  # noqa: E402
from open_guji_cv.core.workspace import set_workspace_override  # noqa: E402

WS = Path(__file__).resolve().parents[2]    # 本仓根＝工作区
set_workspace_override(str(WS))
assert book_code.load(WS) is not None, f"{WS}/code/code.yaml 读不到"
