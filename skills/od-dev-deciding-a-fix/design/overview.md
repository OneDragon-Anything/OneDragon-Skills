# od-dev-deciding-a-fix · 设计概览(what)

## 为什么做
已报告的 bug,"定位根因"的通用调试纪律见 `od-dev-write-operation`(读日志先行 / 假设驱动 / 一次只改一个变量),"决定怎么修"却缺一个系统决策框架。常见失败:直接采纳 issue 里用户给的方案、根因挖得不够深(误判方案临时/永久)、介入点前提没验证。本 skill 把"决定怎么修"锚定到业界方法论(RCA / Impact Analysis / Trade-off Matrix / Hypothesis-driven Verify),给一个可被 review 的决策流程。

## 定位与边界
- 管:从"故障机制已知"到"选定并验证修复方案"的决策。
- 不管:定位故障机制(→ 通用调试纪律 `od-dev-write-operation`;项目专属排查判据 → 所在项目调试类 skill);新功能设计。

## 构成(五步决策流程)
SKILL.md 正文给出 5 步可执行指令,每步锚定一个业界方法论:
0. 确认故障机制(入口)。
1. 画因果链(RCA / 5 Whys / Fault Tree)—— 停在 actionable 层(有权且能修的那层)。
2. 影响面 + 可行动性(Impact Analysis / Blast Radius)。
3. 候选方案(Intervention Selection)。
4. 前提验证 + 权衡(Trade-off Matrix)—— 必填:根因链的「上游修复状态」。
5. 假设驱动验证(Hypothesis-driven Verify)。

## 落点(仓库约定)
- 公共仓 `OneDragon-Skills/skills/od-dev-deciding-a-fix/`(自 SR 仓 `sr-od-dev-deciding-a-fix` 迁入泛化),OneDragon 系列通用。
- 消费方式见仓 `docs/setup/ai_coding.md`(npx skills add 标准安装 / 本地开发 junction)。
- 结构:SKILL.md(入口,方法论 / 判据)+ design/(overview + decisions ADR)。

## 自身一致性
遵守 `od-dev-writing-skills` 4 条硬规范:
- **规范 1**:有 `design/`(design 与 ADR 分开);设计 what 在本文件,ADR 仅经用户命令创建,当前无 ADR,决策 why 归本文件动机段与 git 历史。
- **规范 2**:SKILL.md 指令式(祈使句 + 判据)。
- **规范 3**:自包含 —— 引用全在本仓已提交内容内(`od-dev-*` 兄弟 skill 写全名),不引目录外文件、不引 memory / gitignored(原 superpowers 指针已随迁移去除)。
- **规范 4**:SKILL.md 只写方法论 / 判据,具体案例(pywin32 #2428)不进 always-on 正文。

## 当前状态(GREEN)
- **draft**(GREEN-pending):按 od-dev-writing-skills「两类 skill」,本 skill 为**方法论覆盖型**,RED 可省;**GREEN utility test 尚未跑**(跳过 GREEN 却声称合规 = 违规,故诚实标 draft)。
- **GREEN 方法**(待跑):起干净上下文子 agent,给一个真实 bug 决策任务(如 pywin32 #2428 同型场景),扮用户只答所问、不替做,观察 agent 能否自主走完 5 步并产出可 review 的决策,记 gap → RCA 过滤 → 修 skill → 循环(见 od-dev-writing-skills `references/skill-testing.md` §2)。
- baseline(pywin32 #2428)已跑,价值不在「证明 skill 必要」(那是纠正型用法),而在沉淀两个必填槽位的论证。
