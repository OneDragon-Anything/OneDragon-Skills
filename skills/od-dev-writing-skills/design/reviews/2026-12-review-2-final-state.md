# 独立评审报告 2:大改终态复审(2026-12)

> 评审对象:SKILL.md 七节重写版 + 拆迁后 references(writing-craft 已删)。四维度:全目录一致性 / 名实相符 / 清晰度(重点加权)/ 官方对照(辅)。报告要点存档,处置见文内标注与 design/overview.md 台账。

## 高

### H1 GREEN 术语链断裂 + 死引用 +「完成」口径冲突
- skill-testing 指「GREEN 不可省」但 SKILL.md 全文无 GREEN 定义;「GREEN 不可省」vs「排版/错字不必测」字面冲突;「完成」语义两处不一致。
- 处置:已修——SKILL.md §6 补 GREEN/RED/draft/validated 定义 +「完成」口径单句;skill-testing 头部改为引用式(何时测单一源在 §6)。

### H2 description 漏「测试/验证 skill」正文场景
- §6/§7 测试职责面无触发词,「帮我测一下这个 skill」落在空白带。
- 处置:已补(中文场景 + 英文 test/validate a skill)。

### H3 description 无兄弟外路由,且重叠兄弟已单向路由指来
- od-dev-writing-agent-instructions 已路由「写 skill」过来,本 skill 未回指仓内兄弟(与用户裁定的 superpowers 豁免不同性质,报告标待确认)。
- 处置:已补「写 AGENTS.md / CLAUDE.md 类入口文件 → od-dev-writing-agent-instructions」。

### H4 references 违反「章节从 1 开始」硬规则,overview 自检声明与事实不符
- skill-testing 从 §0 起编、skill-feedback 无编号,overview 却声称「序号 ✓」。
- 处置:已修——两文件重编号(1 起);overview 自检声明修正并注明扫描范围;连带清偿 deciding-a-fix 对 testing §2 的引用(→§3)。

## 中

- M1 SKILL.md §6 与 testing 双源表述漂移(约束配错信号 2 版 vs 4 版;选型判据两种措辞;rationalization 中英混用)→ 已修:§6 补全 4 信号为单一源,testing 改引用式,术语统一「合理化原话」。
- M2 未定义缩写/自造术语群(SSOT / RCA 首现 / arc42 §9 / MADR / 外路由自路由 / bbox / GREEN)→ 已修:逐词补解释或换白话,SSOT 改「单一事实源」,bbox 例改白话,arc42/MADR 处理。
- M3 「一条龙」「本仓」对跨仓安装读者无定义,三分场景下指代漂移 → 已修:开头补自我介绍(OneDragon 定义 + 「本仓」指代)。
- M4 「加到第 5 条『例外』」歧义 → 已改白话(同一条规则下例外条款累积到第 5 个)。
- M5 必做序列 checklist 未放「开头」与 §3.2 字面冲突 → 已补调和句(总装章 checklist 随章文末不算违反,头尾不变量优先)。
- M6 防过时四档单行塞四项自造复合词 → 已拆四行编号列表,CI 改「持续集成脚本」。
- M7 「一步消费的状态」过度压缩 → 已改白话。
- M8 design/README 死标记(「4 条硬规范」描述)+ 漏列第三个 reference → 已重写。
- M9 台账裸编号(M/H/L)不可回溯 → 已修:两份评审报告存本目录,台账引用路径。

## 低

- L1 步骤 7 依赖 evals/TESTS.md 但首轮不存在的分支未写 → 已补(首轮无 TESTS.md 仅验正例)。
- L2 行内顿号并列多处,列表规则缺豁免边界 → 已补(行内短语举例豁免;独立可执行项必须列表)。
- L3 「官方」未指明是谁 → 已改「Anthropic 官方 skill 文档」(首现全称)。
- L4 中英混杂残留(sub-agent / caveat / mechanics / nuance / harness / append-only)→ 已逐处处理。
- L5 design-docs §4 标题自造词 → 已改判据句。
- L6 目录树与自身结构不一致(design/README 在树外)→ 已在 README 索引中显式列出(design/ 存档含 README 与 reviews/)。
- L7 官方对照:实质遗漏很少;500 行红线未显性吸收 → 已补进 token 效率条。

## 待确认处置

- H3 的仓内兄弟路由:报告标「如属用户裁定请降级」——按 §3.1 硬规则(对方已单向路由)加了回指,未按用户既有豁免(superpowers 生态外)处理;如不应加可撤。
- L6 的 design/README 合法性:按「design/ 是维护者档案、不进 agent 上下文」边界处理(树中该行注释已含 README)。
