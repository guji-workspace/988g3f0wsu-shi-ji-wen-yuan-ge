
## 跑批清单（SJ 跑批线程维护）
- why 模板要写：cv 版本（钉 tag）、manager 版本、-w 书仓根、code: k<N>、中心库 db_rev、glyph_pin、corpus、起点步、不带 DRIFT。
- 导出或推 book-text 前：guji-manager ≥ v0.4.31（含 #429 写首选字、#432），导出后校验 F-OV-16、F-OV-05。book-text 每格只录首选字；待审信息、候选、人裁事件都在 KV，不写 pending_reason、不出 decision.json（book-text docs/design/2026-11-book-text只录首选字.md）。只走 KV 的跑批不受影响；史记 book-text 暂不推。
- 交单前 Ops dry-run 核 base 包取得到；出包后核标签、manifest 的 cv/db_rev、页失败（与年表跳页分开计）、human_chars 无报错、人工定框列格位一致。
- 书仓 main 有新提交（尤其 code/ 改动或 k<N> 升版）要通知 Console 重置服务器上的书仓检出（11-09 旧检出缺 code/ 致控制台 500）；标 main 后通知 Console 时，除包标签外写明书仓 main 最新提交号。
- book-text 版本记录（Sheldon 11-10 定）：各书不再写 CHANGES.md，版本记录写进提交信息——bump_original.py 打印的「版本记录:」行原样放进提交信息，带 r 号或 GUJI 卡号（史记写 r 号＋GUJI-750）；本地 book-text 检出不能浅克隆。
- 版本：r24 之后下一轮 spec 的 cv 钉 v0.6.35（main 959f8f5267d1），manager v0.4.34（执行机与本机）；在此之前的换单会把待审首选字写进已有字的格（A31 11-10）。
