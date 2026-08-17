# 0004 run 被停死因四层排查序

- **状态**:accepted
- **日期**:2026-08-17

## Context

自家停机钩子(游戏恰停在触发屏)把每个新 run 在数秒内停掉,诊断者连续 8 轮误判「外部会话拦截」并 blocked goal:①没读死亡时刻日志(钩子停机行每停一次都在写);②「人工结束」标签被当死因证据(框架对任何 stop_running 统一打此标签);③sentinel flag 反复出现、连删 5+ 次仍称「孤儿残留」(「孤儿」与「反复重现」互斥);④连接数 / 均匀时序触发外部归因(工具管道 / 连接池 / 子代理各建连可解释;自家代码也是机器)。根因之一在钩子教学示例:runtime-craft 的 sentinel 教的正是 `write_text(state)` 裸态名,对后来者零信息。

## Decision Drivers

1. 排查序必须由近及远、外部归因需正向证据——反思性归因(「不是我」)最易跳层。
2. 修下游(排查序)不修源头(教学示例的裸态名)会复发。
3. 公共 skill 泛化:不提具体项目钩子名 / 会话细节。

## Considered Options

- **只加 debug-automation 排查序**(否决:钩子示例的裸态名 sentinel 是缺口源头,不修源头只修下游,下一个裸态名 flag 又一轮误判)。
- **只改 write-operation 钩子节**(否决:排查序缺位仍会让诊断者在「1-4 层」里即兴跳外部归因)。
- **两处联动 + 边界指针**(采纳):debug-automation §1 四层排查序 + §4「反复出现的产物=活的生产者」纪律 + description 检索词;write-operation runtime-craft 钩子节 sentinel 自描述规范 + 「删钩子≠删 flag」+ 埋钩子前置评估;write-operation 边界节指针(开发场景检索不到 debug skill)。

## Decision

按采纳方案落地。四层序:死亡时刻日志 → grep stop_running 全调用点(自家钩子优先;「人工结束」标签非证据)→ sentinel 写入者 grep → 外部归因(需正向证据;连接数 / 均匀时序不构成)。钩子节:sentinel 内容自描述(含「我的钩子停的 + 位置 + 收尾动作」,禁裸态名)+ 停机写带特征日志行 + 收尾清单(删钩子代码 + 删 flag + ruff)+ 埋钩子前确认游戏不在触发屏。
