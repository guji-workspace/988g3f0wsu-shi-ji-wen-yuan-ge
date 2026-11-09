
## 跑批清单（SJ 跑批线程维护）
- why 模板要写：cv 版本（钉 tag）、manager 版本、-w 书仓根、code: k<N>、中心库 db_rev、glyph_pin、corpus、起点步、不带 DRIFT。
- 导出或推 book-text 前，guji-manager 须 ≥ v0.4.31（含 #429 写首选字、#432）；只走 KV 的跑批不受影响（A31，2026-11-09）。
- 交单前 Ops dry-run 核 base 包取得到；出包后核标签、manifest 的 cv/db_rev、页失败（与年表跳页分开计）、human_chars 无报错、人工定框列格位一致。
