# 0003. 循环驱动玩法用 node-per-op(flat loop 的结构性卡死缺陷)

- **Status**: accepted
- **Date**: 2026-08-05

## Context

`od-dev-write-operation` 原「拆节点」方法论只覆盖**单 op 内**怎么拆节点(一节点 = 一类画面 / 一个动作),没覆盖**循环驱动玩法**更高一层的结构选型:外层 loop 不断跑、每轮重新发现"现在在哪种状态"再推进的玩法(自走棋对局 / 肉鸽一层 / 多阶段流程),op 结构有两套相反做法:

- **flat loop**:外层一个 loop,每轮 截屏 → 一条优先级阶梯分类"在哪种状态" → 命中 handler → `round_wait` 重跑。
- **node-per-op**:一个 op 拥有一个逻辑单元的完整生命周期;外层只分类 + 委派。

没有判据 → 写循环驱动玩法的人默认拍 flat loop(更直观),但 flat loop 对**有逻辑单元生命周期 + 单元内多阶段**的玩法有一个**结构性卡死缺陷**(非个别 bug):

1. 把"我在哪种单元"和"这单元的哪一步"两条正交问题塞进同一条优先级阶梯 → LCS 噪音 / 优先级脆弱。
2. **无单元作用域卡死判据**:handler 完成不了自己单元时(如 2 步单元只做了第 1 步)仍可能 `round_success` 返回 → 外层 `round_wait` 不增 retry → retry 永不计 → 一直转到 MAX_ITER(可能数小时)才超时。flat loop 把"卡死"和"正常推进"都当"再试一次",无法区分 → 一个 handler 完不成就无限烧全局预算。

**实战验证**:某 SR 自走棋对局玩法的原 flat loop 实跑暴露此缺陷 —— 多步节点 handler 只做第一步就 `round_success`,外层 `round_wait` 不计 retry,某类多步节点卡死约 6 分钟、另一类约 18 分钟(屏幕不变、数十次无效 retry),直到 MAX_ITER 才超时。重构为 node-per-op 后,每节点有自己预算 + 完成检测,卡死可判定 bail。(具体见该玩法的决策日志,本 ADR 不引跨仓 / 本地路径。)

## Decision Drivers

- **方法论正确**:skill 要给循环驱动玩法的结构选型判据,不能只给单 op 拆节点。
- **防结构性卡死**:flat loop 对多阶段单元玩法的卡死缺陷是通用的(换游戏/换玩法一样),必须给判据 + 反模式,让作者选前就知道。
- **保鲁棒**:node-per-op 不能是盲目顺序执行(丢 flat loop 自愈性)→ committed-but-verifying 模式既拥有生命周期又每步重核,是 flat loop 的结构化升级。
- **单源**:循环驱动结构方法论归 write-operation(op 粒度地基);gameplay-automation 引用不双写。

## Considered Options

1. **补 node-per-op 方法论 + committed-but-verifying + 节点预算判据**(选中):给结构选型判据 + 反模式 + 模式,作者选前就知道何时该拆。
2. **只补"flat loop 会卡死"警告,不给替代结构**:作者知道会卡死但不知道怎么改 → 还是自己摸。
3. **不补(认为 flat loop 够用)**:多阶段单元玩法 flat loop 结构性卡死已实证,不补 = 让每个新玩法踩一遍。
4. **归 gameplay-automation 而非 write-operation**:op 结构选型是 op 粒度(怎么划分 op),归 write-operation(ADR-0001/0002 已定 op 粒度地基在此);gameplay 给生命周期视角 + 引用。

## Decision

选 **1**:

- **SKILL.md** 加紧凑节「循环驱动玩法:flat loop vs node-per-op」—— 结构选型判据表 + node-per-op 三件套(两条正交问题分开 / committed-but-verifying / 节点作用域预算)+ 边界检测先于结构,指针到 reference。
- **新增 `references/loop-driven-op-structure.md`**:完整方法论(flat loop 卡死缺陷分析 / committed-but-verifying 伪码 / round 结果映射单元生命周期 / 反模式 / 迁移策略)—— 循环驱动 op 结构 single source。
- **gameplay-automation**:协作 skill 节加指针(循环驱动 op 结构 → write-operation),不双写。

## Consequences

- **正向**:循环驱动玩法作者拿到结构选型判据 + 防卡死模式;node-per-op committed-but-verifying 既拥有生命周期又保鲁棒;op 级循环结构方法论 single source。
- **负向**:SKILL.md always-on 略增(~18 行结构判据,值 —— 结构选错 = 结构性卡死,代价远高于多读 18 行)。
- **边界**:本方法论管"循环驱动玩法怎么划分 op 结构",不取代单 op 拆节点(一节点=一类画面),也不取代 gameplay-automation 生命周期编排(阶段 0-9 仍在它)。
- **follow-up**:GREEN 验证 —— 写循环驱动玩法时是否触发本节 + 选对结构。

## Links

- 相关:`../overview.md`(范围 IN)/ [0001](0001-split-by-granularity.md)(粒度拆分)/ [0002](0002-exploratory-spine-op-level-consolidation.md)(op 级方法论归本 skill)
