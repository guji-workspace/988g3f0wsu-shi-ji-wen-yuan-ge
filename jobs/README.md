
## 跑批清单（SJ 跑批线程维护）
- why 模板要写：cv 版本（钉 tag）、manager 版本、-w 书仓根、code: k<N>、中心库 db_rev、glyph_pin、corpus、起点步、不带 DRIFT。
- 导出或推 book-text 前：guji-manager ≥ v0.4.31（含 #429 写首选字、#432），导出后校验 F-OV-16、F-OV-05。book-text 每格只录首选字；待审信息、候选、人裁事件都在 KV，不写 pending_reason、不出 decision.json（book-text docs/design/2026-11-book-text只录首选字.md）。只走 KV 的跑批不受影响；史记 book-text 暂不推。
- 交单（Sheldon 11-10 定）：史记自己直接向任务库交单，不再请 Ops 代交——`python -m guji_manager.jobs submit`（先 dry-run 核 base 包取得到；需 JOBSDB_TOKEN／JOBSDB_PASSWORD 读写令牌，放会话环境变量，不进仓不进聊天）；base 一律写带 jobNNNN 的完整标签。
- 出包后核标签、manifest 的 cv/db_rev、页失败（与年表跳页分开计）、human_chars 无报错、人工定框列格位一致。
- 书仓 main 有新提交（尤其 code/ 改动或 k<N> 升版）要通知 Console 重置服务器上的书仓检出（11-09 旧检出缺 code/ 致控制台 500）；标 main 后通知 Console 时，除包标签外写明书仓 main 最新提交号。
- book-text 版本记录（Sheldon 11-10 定）：各书不再写 CHANGES.md，版本记录写进提交信息——bump_original.py 打印的「版本记录:」行原样放进提交信息，带 r 号或 GUJI 卡号（史记写 r 号＋GUJI-750）；本地 book-text 检出不能浅克隆。
- 版本：r32 起 cv 钉 v0.7.1（8cf4ff7）＋code: 2（k2，书仓 a8c78ac；中心库 book_defaults 已改 code: 2，rev 943666），manager ≥v0.4.35；v0.7.x 配 k1 拒跑，v0.6.x 配 k2 也跑不了。v0.7 起模型走 R2，交单前核 GUJI_DATA_TOKEN 能从密钥仓解出。字形库撤借库（workspace.yaml glyph_lib: {}），钉 g10。（r28–r31：v0.6.38＋k1）
- 下一轮（r33 起）钉 cv v0.7.2（或 v0.7.3）＋manager ≥v0.4.40（A31 11-10：0.4.40 取代 0.4.38，与 v0.7.2/0.7.3 配套；所修问题只涉 book-text，史记尚未推），两者必须一起升（A31 11-10）：manager 低于 0.4.37 时 v0.7.2 遇增删格报 ImportError 退出；row_segment 不过期。本机检出和执行机都要到 0.4.37。增删格落 book-text 的口径见 guji-manager doc/02-精校/换包落book-text-增删格.md。
- 换包落 book-text 过 R1 闸（manager ≥0.4.38）：字形库刻例的格键在新包里找不到就停。格号变动大（切分改动、增删格）的一轮，标 main／落 book-text 前先核字形库刻例格键与新包对得上。改字形库钉号用 book_overrides.glyph_pin、从 glyph_match 起，不改册 yaml。
- 设计人审记账、book-text 导出、出单等新流程前，先读总纲 guji-manager doc/00-总览/待审单-人裁事件-book-text格子.md（#449，Sheldon 11-10：所有设计围绕这三样）：book-text 格子＝现状（只录首选字），待审单＝问题（中心库 feedback/lists/proofing，整张重出、改单不动 book-text），人裁事件＝答案（只追加，靠锚重绑，机器不改）。

## 直接交单（2026-11-23 改：任务库在 Cloudflare D1）
任务库 11-23 起在 Cloudflare D1（`guji-jobs`），Neon、wss 桥（relay.open-guji.com/jobsdb）、旧美国机 Postgres 都不再用。**令牌只用 `JOBSDB_TOKEN`，别设 `JOBSDB_URL`**；也不再需要 `GUJI_REQUIRE_JOBSDB`。令牌不要打印、不要写进聊天／文档／提交。

1. 载入令牌：`eval "$(python3 /home/user/guji-dev-secret/gsecrets.py export)"`（先 `add_repo` 密钥仓 `sheldonlidev/guji-dev-secret`，克隆到 `/home/user/guji-dev-secret`），用 `[ -n "$JOBSDB_TOKEN" ] && echo set` 核对，只看是否 set。
2. 版本：guji-manager 用正式 tag ≥0.6.2（0.6.1 标 main 必挂）；史記仍在 cv 0.7.x patch 线，**不能用 `guji pipeline <命令>` 五步前缀（要 cv ≥0.9.0）**，一律用下面的老写法。manager 0.6 配 cv 0.7.x 不会被拦。
3. 交单（在书仓根）：
   ```
   export GUJI_JOBS_WHO=SJ-batch          # 收尾通知按这个登记名送；会话换了要重登 register.py SJ-batch --account a
   guji job precheck --books 01-42 --cv <ver> --code <k> --glyph-pin <g> --corpus <n>   # 逐册生效钉子，不一致退出 1
   guji job workers                        # 看执行方在线
   guji job ls --book-id 988g3f0wsu
   guji job submit --book 15 --book-id 988g3f0wsu --cv <ver> --pipeline keben_body_v2 \
       --from <步> --pages all --base <带 jobNNNN 的 main 包标签> --change <改动名> --priority 50 --dry-run   # 先 dry-run
   guji job submit …（去掉 --dry-run 真交）
   guji job show <号> / wait <号> / retry <号> / stats --book-id 988g3f0wsu
   ```
4. 收轮与标 main：`guji round-check <册> --pack <候选> --ledger auto --ledger-book 史記 --set seg_defect=true`（或交 `--kind roundcheck` 单）；存包 `guji products pack push`，标 main `guji products pack promote`（manager ≥0.6.2）；落文本 `guji collect … --no-ai`。
5. 注意：
   - 整书轮一律显式 `--pages all`（`--pages auto` 缺省已关）；逐册 `--book` 交。
   - 判重指纹只算 spec 文本；中心库配置变了 spec 不变会被判 duplicate，再交加 `--again`。
   - `--cv` 必须是正式 tag；`ws_repo` 写本书仓；base 用带 jobNNNN 的完整标签。
   - 任务库不做：标 main、覆盖正式产物、推册配置——这些仍按总览规矩手动做。
   - **收轮必查「每步页数非 0」**（2026-11-26，GM2 查出）：v0.2 整书轮 #16777（11 册）、#16794（28 册）、#16800（34 册）、#16857（31 册）记成功，但执行机复用准备后本机原图缺，`--pages all` 解析成 0 页，每步都是 0 页；存下的包其实是底包换了个名字，又被标了 main，后面的换单、小轮都接在上面。框架修复在 guji-manager #1056。以后每张 rerun 单，roundcheck 之前先 `guji job show <号>` 核两处：输出里的 `完成：<步> ok N` 要 N>0，不能是空的「完成：」或「：0 页」；run 段的用时也要合理（整册从 column_warp 起只跑一两分钟就是可疑）。核不过的不收轮、不标 main，原样整册重交。
   - 11-22 已删 `release`、`deploy`、`batch`、`label-batch`、`cards`、`store`（store 改 `guji db push`）。

## k1→k2 切换记录（2026-11-10，r32）
- 内容：row_segment 四个书级开关（seal_inkcut、seal_gap_slots_empty、jiazhu_free_split、jiazhu_step_split）从 cv 删掉，实现搬进书仓 code/（seal_ink.py、jiazhu_step.free_split），出 k2（PR #1，合并提交 a8c78ac 打 tag k2）。
- 验等价：先逐字比 diff（与 cv v0.6.38 原实现只差导入路径、常量出处）；再在本机用含钩子的 cv dev＋PR 的 code/，设 `GUJI_CODE_DRIFT=warn`、`--override '{"code":2}'`，把 main 包铺进临时工作区（products/<册>/…，data_full 链到原图），`guji step row_segment --pages … --force --no-prep` 重跑，和 main 包比：02 册 6 页、05 册 4 页（含 p2 印泥页、02:13/58 夹注 free_split 页）逐字节相同。证据登进 code/equiv.yaml，cv 侧 row_segment 不过期，所以全书重跑从 glyph_match 起就够。
- 换钉顺序：合 PR → 打 k2 → 中心库 book_defaults `code: 2`（db push --no-admit）→ spec 钉 cv v0.7.1 → 交单。已排着的 v0.6.38 单要先取消（#1823–#1832），否则新配置下会拒跑或出两套包。

## steps.from 不能写 border_detect_gate（11-13）
r53 首交 11–42 册写 `from: border_detect_gate`，pipeline 报 ValueError 全挂（#2756–#2787）。闸挂在 border_detect 出口会自动跑，要从切分最早步重跑一律写 `from: border_detect`。
