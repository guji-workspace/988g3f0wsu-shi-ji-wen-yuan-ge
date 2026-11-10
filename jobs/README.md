
## 跑批清单（SJ 跑批线程维护）
- why 模板要写：cv 版本（钉 tag）、manager 版本、-w 书仓根、code: k<N>、中心库 db_rev、glyph_pin、corpus、起点步、不带 DRIFT。
- 导出或推 book-text 前：guji-manager ≥ v0.4.31（含 #429 写首选字、#432），导出后校验 F-OV-16、F-OV-05。book-text 每格只录首选字；待审信息、候选、人裁事件都在 KV，不写 pending_reason、不出 decision.json（book-text docs/design/2026-11-book-text只录首选字.md）。只走 KV 的跑批不受影响；史记 book-text 暂不推。
- 交单（Sheldon 11-10 定）：史记自己直接向任务库交单，不再请 Ops 代交——`python -m guji_manager.jobs submit`（先 dry-run 核 base 包取得到；需 JOBSDB_TOKEN／JOBSDB_PASSWORD 读写令牌，放会话环境变量，不进仓不进聊天）；base 一律写带 jobNNNN 的完整标签。
- 出包后核标签、manifest 的 cv/db_rev、页失败（与年表跳页分开计）、human_chars 无报错、人工定框列格位一致。
- 书仓 main 有新提交（尤其 code/ 改动或 k<N> 升版）要通知 Console 重置服务器上的书仓检出（11-09 旧检出缺 code/ 致控制台 500）；标 main 后通知 Console 时，除包标签外写明书仓 main 最新提交号。
- book-text 版本记录（Sheldon 11-10 定）：各书不再写 CHANGES.md，版本记录写进提交信息——bump_original.py 打印的「版本记录:」行原样放进提交信息，带 r 号或 GUJI 卡号（史记写 r 号＋GUJI-750）；本地 book-text 检出不能浅克隆。
- 版本：r28 起 cv 钉 v0.6.38（eafd98e1），manager ≥v0.4.35（执行机与本机）。改字形库钉号用 book_overrides.glyph_pin、从 glyph_match 起，不改册 yaml。
- 设计人审记账、book-text 导出、出单等新流程前，先读总纲 guji-manager doc/00-总览/待审单-人裁事件-book-text格子.md（#449，Sheldon 11-10：所有设计围绕这三样）：book-text 格子＝现状（只录首选字），待审单＝问题（中心库 feedback/lists/proofing，整张重出、改单不动 book-text），人裁事件＝答案（只追加，靠锚重绑，机器不改）。
