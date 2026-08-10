# 0007. 跨玩法偏离的运行时恢复(loop 调度层):bot 自主运行遇偏离 → 导航回目标,不停

- **Status**: proposed
- **Date**: 2026-08-11

## Context

`od-dev-screen-onboarding` ADR-0016 补了「跨玩法偏离协议」的**调试 / 建档角度**(dev 遇偏离怎么手动导航回 + 把恢复路径建进 screen_info / doc),并在边界节显式标注:**bot 无人值守自主运行时遇跨玩法偏离自动导航回 → gameplay-automation(待补)**。

本 skill 此前缺这个**运行时调度角度**。runtime-iteration.md §事件长尾的兜底是「任何匹配不到的状态走 fallback(点空白 / ESC)」—— 但 bot 偏离到非目标玩法时,通用 fallback(点空白 / ESC)会让 bot 卡在错玩法里反复转,导航不回目标;且没有「这是跨玩法偏离 → 该导航回」的分派分支,bot 只会 stall / 盲重试同一偏离画面。

根因:loop 的未匹配状态分派没把「跨玩法偏离」单列为一类恢复(区别于「目标玩法内未建档事件」)→ 落进通用 fallback / stall。

用户原则(2026-08-10):「就算偏离到别的玩法,也要想办法导航回目标玩法,而不是停」。适用 dev(screen-onboarding,已补)+ runtime(本 ADR)。

通用 gap:任何玩法自动化 bot 无人值守跑都可能偏到别的玩法(误点跨玩法入口 / 上次残留未退 / 用户手动切走)→ 同样会 stall / 盲重试。非某玩法 / 模型特异。

## Decision Drivers

- **bot 自主性**:偏离是可恢复运行时状态,导航回目标是 bot 职责,不是 stall / 停 / 等指示理由。
- **与「目标玩法内未建档事件」区分(分派不同)**:未建档事件 → 加 handler(§事件长尾);跨玩法偏离 → 导航回目标。不区分 → 拿通用 fallback 点空白 ESC,卡错玩法。
- **与「任务进度防偏离」区分(维度不同)**:progress-tracking §2 防偏离门是 **dev 焦点纪律**(别漂离主线工作);本 ADR 是 **bot loop 运行时**调度恢复。不同维度,须显式区分防混淆。
- **复用而非重造**:判定(认知完整但非目标 → 导航回)screen-onboarding 已立;本 ADR 只补 loop 调度层怎么把恢复落进未匹配状态分派,不重复判定 / 不重复建档方法论。

## Considered Options

1. **维持通用 fallback(点空白 / ESC)**:现状;bot 卡错玩法反复转,导航不回目标。**否**。
2. **停,等用户指示**:用户原则明确否决 —— 偏离可恢复,导航回目标是 bot 职责。**否**。
3. **loop 分派先分类,跨玩法偏离 → 导航回目标续(选中)**:未匹配状态先判属目标玩法(未建档事件 → §事件长尾)还是非目标玩法(偏离 → 导航回入口链续)。复用 screen-onboarding 判定,本 skill 补 loop 调度。
4. **只放 screen-onboarding 不放本 skill**:**部分否**。判定 + dev / 建档角度归 screen-onboarding(已补);但 loop 调度层(怎么把恢复落进 bot 主循环的未匹配状态分派)是 gameplay-automation 的实现方法论,归本 skill。两者互补。

## Decision

选 3(+ 4 的归属划分)。

- **runtime-iteration.md** 新增「§跨玩法偏离的运行时恢复(loop 调度层)」:loop 未匹配状态分派先分类 —— 目标玩法内未建档事件(→ §事件长尾加 handler)vs 非目标玩法偏离(→ 退 B 出口 → 枢纽 → A 入口链 → 续工作,禁 stall / 通用 fallback / 停)。复用 screen-onboarding 判定;本节补 loop 调度层。
- **SKILL.md 做法二**加一句指针:loop 运行时须能从跨玩法偏离恢复(导航回目标续,禁 stall / 通用 fallback / 停)→ runtime-iteration.md;并与任务进度防偏离(progress-tracking §2)显式区分。
- **三维度区分**(防混淆):任务进度防偏离(progress-tracking §2,dev 焦点)/ dev 跨玩法偏离(screen-onboarding ADR-0016,dev 建档)/ 运行时跨玩法偏离恢复(本 ADR,bot loop 调度)。

## Consequences

- **正向**:bot 无人值守遇跨玩法偏离不再 stall / 卡错玩法,自动导航回目标续。
- **负向**:loop 未匹配状态分派多一层分类;导航回目标依赖两个玩法的入口 / 出口路径都已在画面档案建模(未建档 → 不能自动恢复 → 记日志 + 上报,别盲循环;触发 screen-onboarding 补建档)。
- **边界**:判定 + dev / 建档角度(偏离怎么手动导航回 + 建进 screen_info / doc)归 screen-onboarding ADR-0016;本 ADR 只管 loop 调度层运行时恢复。任务进度防偏离归 progress-tracking §2。
- **follow-up**:GREEN 验证 —— 用本方法论指导实现的 loop,无人值守跑遇跨玩法偏离时是否自动导航回目标续(而非 stall / 通用 fallback)。

## Links

- `od-dev-screen-onboarding` ADR-0016(跨玩法偏离协议:判定 + dev / 建档角度;本 ADR 补其边界标注「待补」的运行时角度)。
- [../runtime-iteration.md](../runtime-iteration.md) §事件长尾(被本 ADR 扩展的 loop 兜底分派)+ 新增「§跨玩法偏离的运行时恢复(loop 调度层)」。
- [./INDEX.md](./INDEX.md)。
