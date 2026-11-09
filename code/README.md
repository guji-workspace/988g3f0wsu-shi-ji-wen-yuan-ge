# 书级代码（code/）

本书专属的切分代码，2026-11-09 从 open-guji-cv 搬来（cv 设计：`doc/design/书级代码.md`）。cv ≥0.7.0 把本目录挂成
`guji_book.<name>`（`code.yaml` 的 name），按 `overrides` 替换刻本缺省实现里的同名模块；没覆盖的照走 cv 的。

- 改代码：只许 import `open_guji_cv.seg`、`open_guji_cv.book_api` 与本目录模块（`guji code check -w <本仓根>` 查）。
- 发版：本仓提交 → `guji code release -w <本仓根>` 出 `releases/k<N+1>.json` → 提交、推 main → 打 tag `k<N+1>`（本地 `git push origin k<N+1>`；云端走 ai-team 中转站 `python3 process/tag.py guji-workspace/<本仓> <40 位提交号> k<N+1> "说明"`，只认 main 上的提交）→ 书配置写 `code: N+1`。
- 测试：`python -m pytest code/tests -q`（要可编辑安装的 cv，借它 `tests/helpers`）。
- 代码等价：`equiv.yaml`（搬家/只改 import 时登记，让产物不过期）；之后真改了模块，产物照常过期。
