# ADR-0008:三类工作定义上移 progress-tracking,autonomous-mode 只留机械化触发器

- Status: accepted
- Date: 2026-08-25

## Context

用户问「三栏是否无论自主推进都该关注」——答案是对的:主线/发现轨/持续流程是**普适关注框架**(指导模式下 review 该做还是该做、测试基线还是要绿),自主模式改变的只是触发方式(人自觉→提醒网机械化)。此前定义装在 autonomous-mode 里,隐含「只有自主模式才需要发现轨」的错误前提。

## Considered Options

- **定义留在 autonomous-mode(维持现状)**:否决——认知框架错装进自动化 skill;指导模式的会话读不到它,progress-tracking 治理进度文件时也不知道三栏的语义来源。
- **两边各写一份**:否决——双源必漂移(违反两 skill 已声明的引用纪律)。
- **定义上移+触发器留守(选中)**:progress-tracking 增「三类工作是普适关注框架」条款(含完整定义与三栏规格);autonomous-mode 的表改为摘要+指向,本 skill 特有的部分(依赖驱动补位/四来源周期扫描/健康监控)保留并显式标注「这是自主模式的机械化」。

## Decision

progress-tracking §1 增普适框架条款;autonomous-mode §3 三类工作表改为「摘要+触发机制」两列,边界声明置顶。判据:**progress-tracking 回答「该关注什么」,autonomous-mode 回答「没人盯时怎么保证关注到」**。

## Consequences

- 正:指导模式/非自主会话也获得该框架;三栏规格单一源;两 skill 职责更纯(认知 vs 自动化)。
- 负:autonomous-mode 读者需跳转拿完整定义——由摘要+显式指向缓解(表内信息足够日常运转)。
