# 循环驱动玩法的 op 结构(flat loop vs node-per-op,reference)

> 本 skill(`od-dev-write-operation`)的 situational reference。SKILL.md 给结构选型判据 + 模式名;本文件给完整方法论(为什么 flat loop 会卡死 / committed-but-verifying 伪码 / round 结果如何映射单元生命周期)。`od-dev-gameplay-automation` 的生命周期视角也引用本文件(单源,不重复)。

## 何时 flat loop / 何时 node-per-op

「**外层 loop 不断跑、每轮截图重新发现"现在在哪种状态"再推进**」的玩法(自走棋对局 / 肉鸽一层 / 多阶段流程 / 任何带主循环的自动化),op 结构有两套相反做法,选错会结构性卡死:

| 结构 | 形状 | 适用判据 |
|---|---|---|
| **flat loop** | 外层一个 loop:每轮 截屏 → 分类"在哪种状态"(一条优先级阶梯) → 命中 handler → 推进 → `round_wait` 重跑 | **纯帧级、无逻辑单元生命周期**的反应式推进(点空白加速战斗 / 结算翻页 / 等待型)。每帧独立,无"这个单元做到哪步了"的状态 |
| **node-per-op** | 一个 op 拥有一个**逻辑单元的完整生命周期**(开始→处理→结束);外层只做分类 + 委派 | 流程有**逻辑单元生命周期** + 单元内**多阶段** + 需要**单元作用域的卡死判据**。满足任一即应拆 |

> 判据核心:你的玩法有没有"**逻辑单元**"(有明确开始/处理/结束的块,如"一个节点""一个回合""一个事件")且单元内有**多阶段**?有 → node-per-op;没有(每帧独立反应)→ flat loop。

## flat loop 的结构性卡死缺陷(为什么多阶段单元玩法不该用)

flat loop 把两件事塞进同一条优先级阶梯,是所有优先级脆弱 / 误匹配的根因,且有一个**结构性卡死缺陷**(非个别 bug):

1. **两条正交问题混在一起**:
   - (A)"我在哪种逻辑单元里"(小集合分类,稳定 —— 就那几种单元类型)
   - (B)"这个单元的哪一步"(单元特定的多阶段)
   flat loop 把 (A)+(B) 塞进同一条阶梯 → LCS 噪音多、优先级脆弱、新单元类型要插进拥挤的阶梯。
2. **无单元作用域卡死判据**:flat loop 的 handler **完成不了自己单元时**(如一个 2 步单元只做了第 1 步)仍可能 `round_success` 返回(自以为点完),外层 loop 用 `round_wait`(重跑当前,**不增 retry**)→ **retry 永远不计 → 一直转到 MAX_ITER 才超时**(可能数小时)。flat loop 把"卡死"和"正常推进"都当"再试一次",**无法区分** → 一个 handler 完不成就无限烧全局预算。

→ 流程有逻辑单元生命周期 + 多阶段时,用 node-per-op 把"卡死"变成**单元作用域可判定的**(N 次没完成 = bail)。

### flat loop 合理适用场景内也要守:推进型 handler 完成验证(底线,[ADR-0009](../design/decisions/0009-flat-loop-handler-completion-check.md))

上面讲的是"**有逻辑单元时** flat loop 扛不住,该迁 node-per-op"。但 flat loop 的**合理适用场景**(纯帧级反应式:点空白加速战斗 / 结算翻页 / 点掉弹窗 / 等待型)里,只要 handler 是**推进型**(点一下让画面往前走),仍有同一坑的**另一面**:**点不中(坐标落候选间隙 / LCS 误匹配 / click 没落地)→ 覆盖层 不关 / 没翻页 → loop 下一轮还在本屏 → 又点 → 又没中 → `round_wait` 不计 retry → 无限到 MAX_ITER**。这是 `round_wait` 不计 retry 这一机制的另一种触发(上节是"有单元 handler 完不成",本节是"无单元 handler 点不中")。

**修法**(与 op 边界出口验证 / node op 完成检测同构,三层完成验证的最后一块):**推进型 handler 点了之后必须验画面推进**(目标按钮消失 / 覆盖层 关 / 画面跳 / 锚变化 —— 任一可靠信号,见 `od-dev-screen-onboarding` §3.5);验不到 → `round_retry`(计当前 flat 节点的 `node_max_retry_times`)兜底退出,**别盲目 `round_wait` 重跑**(不计数 → 点不中时无限)。

一句话:**「点了」≠「成了」**。无论点不中的根因是啥(坐标 / LCS / click 异步,见各节),完成验证 + `round_retry` 都是兜底。flat loop 给不了**单元作用域**预算,但推进型 handler 仍能用**当前节点**的 round_retry 预算兜底(N 次没推进 = 判卡死 FAIL,不无限烧全局 MAX_ITER)。这与"有单元生命周期该迁 node-per-op"(上节)**不矛盾** —— flat loop 合理场景内,handler 也要守这条底线;有单元生命周期 + 多阶段时仍该迁 node-per-op。

## node-per-op 三件套(缺一退化成 flat loop 的卡死)

### 1. 两条正交问题分开

- **外层 op(瘦调度器)**:只回答 (A)"进哪种逻辑单元"(小集合分类 + 委派给对应 node op + 接收 bail/完成后 return 再分类)。**不**关心单元内哪一步。
- **node op**:只回答 (B)"这单元的哪一步"(单元内多阶段处理)。

### 2. committed-but-verifying 模式(保鲁棒的关键)

node op **拥有**单元生命周期(刻意驱动已知阶段,不是盲目试探),但**每步重核"我还在这个单元吗"**,被意外弹出(进了下一单元 / 意外 覆盖层 / 已完成)→ **bail 回外层**(return 交还)。

- **不是盲目顺序执行**(那会丢 flat loop 的自愈性 —— 意外弹出时还傻按原顺序点);
- 是"**拥有 + 持续核对**",严格说是 flat loop 的**结构化升级**,不牺牲鲁棒。

伪码(node op 的主循环节点内):
```
每轮(截屏后):
  if 仍在本单元的某一步 → 处理该步(选/确认/...)
  elif 进了本单元的子流程(如战斗)→ 驱动子流程
  elif 已离开本单元(到下一单元 / 别的界面)→ round_success(交还外层)   # ← 保命(bail)
  else → round_retry(计节点预算)
  if 节点内 retry 已超预算 → round_fail/降级(不无限烧)                 # ← flat loop 给不了
```

### 3. 节点作用域预算 + 完成检测(flat loop 给不了的核心价值)

node op 有**自己的 retry 预算 + 完成检测**:
- **完成检测**:单元的"结束"有可锁信号(类型特定:事件类 = 确认后 覆盖层 消失;战斗类 = 战斗结果 + 进下一单元;多步类 = 全步骤完成 + 生效)。
- **预算**:`round_retry` 累计,超本节点 `node_max_retry_times` → 框架转 FAIL。N 次没完成 = **判定卡死 → bail / 降级**(退而求其次:如多步单元某步选不了 → 随便选一个 / 跳过该步),**不是无限 retry 烧全局预算**。
- 预算**按单元算**:一场慢战斗吃的是它自己节点的预算,不再吃整局/整个 loop 的全局 MAX_ITER。

## round 结果如何映射单元生命周期

node-per-op 语境下,round 结果语义(见 `node-graph.md` 的表)对应:

| round 返回 | node-per-op 语义 |
|---|---|
| `round_success` | **本单元完成**,交还外层(外层重新分类"现在进哪种单元")。⚠️ **只有真的完成才返回 success** —— 完成不了用 `round_retry` 或 bail,别"点了一下就 success"(那是 flat loop 卡死的根因) |
| `round_retry` | 计**节点作用域预算**(本节点重试);超 `node_max_retry_times` → 框架转 FAIL |
| `round_fail` | 本节点判定卡死(bail/降级后仍无法推进)→ 沿 fail 边 / op 失败,**不无限烧** |
| `round_wait` | 等画面变化/动画后重跑当前节点(**不增 retry**)|

> **反模式(必踩)**:node op 的某步完成不了(如多步单元的第二步选不了)却 `round_success` 返回 → 外层以为单元完成重新分类,但画面没变还在本单元 → 又进本 node op → 又只做第一步 → 又 success → **无限循环(全局预算烧光才超时)**。修法:完成检测不通过 → `round_retry`(计节点预算)→ 超预算 bail/降级。

## 地基:边界检测先于结构

建 node-per-op **前**,先实地确认:
1. **单元开始信号**:每种逻辑单元的"进入"有可锁信号(OCR 锚点 / 模板 / 固定 area)。不可锁 → 外层分类不准 → node op 误进。走 `od-dev-screen-onboarding` 补画面建档。
2. **单元结束信号**:每种单元的"完成/离开"有可锁信号(类型特定)。不可锁 → 完成检测不准 → 误 success 或无法 bail。

边界不稳,**先补画面建档**再建结构 —— 否则 node op 因边界误判误进误退,比 flat loop 更难调。

## 迁移策略(flat loop → node-per-op,先零件后整体)

已有 flat loop 要重构:
1. 立 node op 基类模式(committed-but-verifying + 节点预算 + 完成检测)。
2. 外层 loop 改瘦调度器(分类 + 委派)。
3. **pilot = 当前活体卡死的单元**(修了立刻能验证 + 解锁观察后续)。
4. 其余 node op 逐个迁移(每迁移一个 `run_operation` 验证一遍)。
