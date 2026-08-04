# 0002. 探索式为主线 + op 级方法论归 write-operation(gameplay 瘦身)

- **Status**: accepted
- **Date**: 2026-08-04

## Context

`od-dev-gameplay-automation` 的 `runtime-iteration.md` 原把"边实现边补分支"框成「肉鸽 / 多分支玩法事件类型巨多 → 事件长尾(stage 8 善后)」。这是**错位**:

自动化脚本开发 ≠ 普通软件工程,根本区别是**需求不可完备**:面对新玩法自动化,**建档(需求)阶段只能摸大概**(主流程 + 主要决策点),玩法的**分支 / 子状态 / 边缘情况(随机事件、条件触发的子界面、过渡叠层、各类结算、失败路径…)建档时摸不清**,很多要实机跑到那个状态才暴露。故工作方式是**建档-led 的探索式增量**(建档先粗 → 实现 → 测试 → 发现未预期 → 补建档 + 补分支 → loop),不是"规格 → 实现 → 交付"。

**「多 log 多截图」的根因**也由此而来:每次实跑都在暴露建档缺口,要从一次跑榨取最多信息,而非跑一次只找一个坑。

这与**肉鸽无必然关系** —— 大部分玩法都有分支(肉鸽只是密)。这是自动化开发的**根本工作方式**,贯穿实现-测试全程,不是某玩法类型的善后阶段。

同时,op 级运行时方法论(信息密度 / 调试读日志 / 预料外画面调研 / 运行时不确定性预留日志 / 重复建op)原本散在 gameplay-automation/runtime-iteration,与 write-operation 的 op 粒度规范**重复**(双源,会漂移)。

## Decision Drivers

- **方法论正确**:skill 要反映自动化开发的真实工作方式(探索式 / 建档-led),不能错框成"肉鸽长尾"。
- **单源 / 不重复**:op 级运行时方法论不能 gameplay + write-operation 双源。
- **地基归位**:op 是最具体单元(写 / 测 op 时撞运行时不确定性、框架踩坑)→ op 级方法论 + 框架踩坑的地基应在 write-operation;gameplay-automation 给生命周期视角 + 引用。
- **落地 ADR-0001 follow-up**:op 级方法论迁入 write-operation 本就是 0001 计划的瘦身。

## Considered Options

1. **探索式为主线 + op 级归 write-operation,gameplay 生命周期引用**(选中):方法论正确框定 + 单源 + 地基归位。
2. **探索式归 gameplay-automation(lifecycle),write-operation 纯 mechanics**:写改修 op(高频,不进 gameplay)的人够不着探索式方法论 + op 级技术 → 回到 0001 的触发错位。
3. **独立"探索式开发"skill**:过度拆分;探索式与"op 该怎么写"不可分(拆小 / 多log / 预料外调研都是 op 级技术),拆出去又得互相引用。
4. **维持现状(肉鸽长尾框 + 双源)**:方法论错位 + 漂移。

## Decision

选 **1**:

- **write-operation**:SKILL.md 开篇加**探索式主线**(建档-led 增量:建档先粗 → 实现 → 测试 → 发现 → 补建档+补分支 → loop;多 log 多截图根因;非肉鸽),作为"为什么 op 要这么写"的地基;新增 `references/runtime-craft.md` 作 **op 级运行时技术 single source**(信息密度 / 调试纪律 / 预料外调研 / 运行时不确定性 / 重复建op);`framework-pitfalls.md` 作**框架踩坑 single source**。
- **gameplay-automation**:`runtime-iteration.md` **重框**为「探索式迭代(生命周期视角)」—— 阶段 1 玩法建档必然粗(需求不完备)→ 阶段 5/8 实现+测试+补分支迭代;**瘦身** op 级技术(调试 / 预料外 / 多log / 重复建op)→ 引用 write-operation 的 `runtime-craft.md`;**删** `framework-pitfalls.md` → 引用 write-operation。
- **未来 application skill**:app 编排也迭代发现分支 → 引用 write-operation 的探索式主线 + runtime-craft。

## Consequences

- **正向**:方法论正确反映自动化开发真实工作方式;op 级运行时方法论 + 框架踩坑 single source(无漂移);gameplay-automation 瘦身(0001 follow-up 落地);写改修 op 高频任务拿到完整地基。
- **负向**:gameplay-automation 用户要跨 skill 拿 op 级技术(靠 SKILL.md 显式指针降低漏读);write-operation always-on 略增(探索式主线 ~150 词,值 —— 它是地基)。
- **边界**:探索式是**开发工作方式**的框定,不取代 mechanics(节点图 / round 结果仍由 write-operation 主体教);也不取代 gameplay-automation 的生命周期编排(阶段 0-9 仍在它)。
- **follow-up**:GREEN 验证两 skill 协作触发(新玩法 → gameplay-automation 生命周期 → 写 op 时 write-operation 探索式主线 + runtime-craft)。

## Links

- 相关:`../overview.md`(定位 / 范围 IN)/ [0001](0001-split-by-granularity.md)(粒度拆分,本 ADR 落地其 follow-up)
- 影响他 skill:`od-dev-gameplay-automation`(runtime-iteration 重框 + 瘦身)
