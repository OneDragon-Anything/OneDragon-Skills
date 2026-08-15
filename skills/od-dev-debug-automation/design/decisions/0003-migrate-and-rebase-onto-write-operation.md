# 0003. 自 SR 仓迁入公共仓 + 基座从 superpowers 换到 write-operation 调试纪律

- **Status**: accepted
- **Date**: 2026-08-15

## Context

本 skill 原名 `sr-od-dev-debug-automation`(SR 仓),标「项目专属判据」。逐节核验后实际层级:§2 节点流转定位(`@operation_node`/`@node_from`)、§3 识别路径分歧(分析工具 vs bot 运行时)、§4 采证、§5 陌生画面刹车 全为 `one_dragon` 框架级;§1 双进程日志分流的**架构**也是框架级(GUI 调度器 vs MCP server),仅日志**路径**(`.debug/sr_od_mcp/`)与 `mcp__sr_od__` 命名空间是 SR 专属。其 overview 自述「源自系列上游项目的一次真实排查,方法论对星铁同样适用」—— 本就系列通用,落在 SR 是历史路径。基座原为 `superpowers:systematic-debugging`(SR 环境标配产物)。

## Decision Drivers

- **框架级通用**:判据锚定 one_dragon 公共包机制(双进程 / run_record / 节点流转 / 识别管线),ZZZ 等姊妹项目同样适用。
- **自包含**(规范 3 硬门):公共仓不引引用闭包外的 skill。
- **与 write-operation 防撞**:两者都从「读日志」开始,需明确分工路由。

## Considered Options

1. **留 SR 仓**:ZZZ 等项目用不上;框架级排查判据是系列级资产。
2. **迁入原样保留 superpowers 基座**:破坏自包含(同 ADR-0003 先例 ×3)。
3. **迁入 + 基座换指 write-operation 调试纪律**(选中):write-operation ADR-0010 刚内联的通用调试纪律(读日志先行/假设驱动/一次只改一个变量)正是原 superpowers Phase 1-4 的等价物,且在本仓内。
4. **并入 write-operation 成一节**:两者触发场景不同(开发中 vs 运行后法证),并入让 write-operation 触发面过宽、正文膨胀。

## Decision

选 3:

- 迁入 `skills/od-dev-debug-automation/`;ADR-0001/0002 原样迁入;SKILL.md 泛化:日志路径 → 「路径按所在项目 `.debug/` 约定」、`mcp__sr_od__` → 「项目 MCP 工具」;`analyze_screen` 保留全名(od-dev-screen-onboarding 先例,框架稳定工具名);`run_record` 路径标注 one_dragon 框架约定。
- 基座指针:superpowers:systematic-debugging → `od-dev-write-operation` 调试纪律;保留 ADR-0001「叠加而非重写」设计,叠加层 = 运行后法证判据。
- **分工路由写进 description**(负向路由):「开发中自己写的 op 卡住 → od-dev-write-operation,本 skill 不触发」;判据一句话:你在写这个 op(开发内循环)vs 拿用户失败反馈排查(事后法证)。
- 与 write-application 的接力交点(判读其产物 `run_record`)不动 —— application 管怎么写记录,本 skill 管怎么读记录排查。

## Consequences

- **正向**:系列项目共享运行 bug 排查判据;与 write-operation / deciding-a-fix / screen-onboarding 形成完整链条(排查→建档→修法决策);公共仓 12 skill 完全自包含。
- **负向**:SR 仓 skills/ 清空,其 AGENTS.md Skills 节需改为公共仓指针(另行确认);GREEN 状态仍 draft(随迁不变)。
- **follow-up**:各项目 MCP server 日志路径放项目自己的入口文件/doc(本 skill 只留「按项目约定」)。

## Links

- 基座:[write-operation ADR-0010](../../od-dev-write-operation/design/decisions/0010-inline-debugging-discipline-drop-superpowers-pointer.md)(调试纪律内联)。
- 同批迁移先例:[deciding-a-fix ADR-0003](../../od-dev-deciding-a-fix/design/decisions/0003-migrate-from-sr-and-drop-superpowers.md)、[pr-review ADR-0006](../../od-dev-pr-review/design/decisions/0006-migrate-from-sr-and-generalize.md)、[pr-finishing ADR-0004](../../od-dev-pr-finishing/design/decisions/0004-migrate-from-sr-and-drop-superpowers.md)。
