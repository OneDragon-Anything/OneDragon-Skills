# 0011. 随机态钩子前置门:reader 须过画面态锚点门才算数(判据与实现两处联动)

## Status

accepted(2026-08-16)

## Context

随机态钩子的分流判据(runtime-iteration 头部)只回答「bot 能否推进 → 选采集还是停机」,没约束 **reader 自身的画面态前置条件**。实战(SR 货币战争,2026-08-16 M37/M38):照 runtime-craft 钩子节标准做法在商店卡牌 reader 上埋停机钩子,reader 无条件裁牌区 rect 做识别;商店**收起 / 未展开帧**上牌区实为节点进度条,reader 全 miss → 钩子把「非法画面态的空读」当「真有未识别卡」→ 误停机 3 次,浪费对局时间 + 误导开发者去补不存在的模板。(SR 侧修复 commit e7bbd711:商店开态门。)

这是所有 reader 钩子的通病:reader 在非法画面态上跑,「缺数据 / 全 miss」是伪信号;钩子无法区分「目标态真出现」vs「reader 在错误画面上空读」。采集钩子同理(非法态存进的是垃圾样本,离线设计 reader 时被污染)。

## Decision Drivers

- 前置门对采集 / 停机两类钩子都必需(误停机 / 垃圾样本同一根因),防线不能只挂一类。
- 钩子知识已分三处:分流判据(本 skill runtime-iteration)= 生命周期判据;采集细作法(`od-dev-screen-onboarding` 随机 / 条件态节);停机细作法(`od-dev-write-operation` runtime-craft 钩子节)= op 级实现 single source。新内容须不破这个分层、不双源。

## Considered Options

1. **只改 runtime-iteration 分流判据**(反馈原案):否决 —— runtime-iteration 自身声明「op 级钩子作法 single source 在 write-operation runtime-craft」;只加判据不加实现步,照 runtime-craft 标准做法写钩子的智能体仍漏门(实战事故正是这条路径)。
2. **只改 runtime-craft 钩子节**:否决 —— 分流判据 blockquote 是采集 / 停机两类钩子的共享入口(采集路径走 screen-onboarding,不读 runtime-craft 钩子节);采集钩子的垃圾样本问题覆盖不到。
3. **两处联动**:分流判据 blockquote 补判据句(两类通用,何时不算数)+ runtime-craft 标准做法加实现步(锚点门先于 reader,代码示例整体包门)+ 两处互引。✓

## Decision

选 3。判据(钩子触发 = 画面态合法 且 reader 检出,缺一不可;锚点不命中 → 空读是伪信号,跳过不停机 / 不写 sentinel / 不存样本)进 runtime-iteration 分流判据 blockquote;实现步进 runtime-craft 钩子节标准做法(步 2,代码示例把钩子整体包进锚点门);两处互引成闭环。

## Consequences

- **正向**:非法画面态上的空读不再触发钩子;采集 / 停机两类钩子同一防线;判据 ↔ 实现互指,任一入口进来的智能体都能看到门。
- **边界**:锚点门依赖该画面已有锚点 area(id_mark / 稳定 area);画面本身未建档时无锚点可用 —— 此时本就不该在该画面埋 reader 钩子(先建档)。锚点怎么选归 `od-dev-screen-onboarding` id_mark 方法论,本 ADR 不重复。
