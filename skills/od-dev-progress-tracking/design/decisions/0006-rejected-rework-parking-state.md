# ADR-0006:打回泊位态 rejected(打回与返工解耦)

- Status: accepted
- Date: 2026-09-11
- Amends: 0004 决策 1 的状态命名——六态扩为七态,新增 `rejected`(=打回已裁决、返工未启动)。0005 的命名判据(态名编码「谁的动作、进行到哪一步」)延续;0004 的多方自记账/账本级锁/文件存在门/返工熔断全部不变。

## Context

pending_review→doing 一跳把「打回裁决」与「返工开工」焊死:reject 之后未必能立刻返工(原 worker 在飞、槽位被占、优先级未到),账本却只能停在 pending_review——「待验收」与「已打回待返工」两种含义挤在一个态里。后果:打回积压不可见,兜底对账分不清「reviewer 没审」和「审了没派」;编排者想延后返工就得让账本说谎。

## Decision

1. 新增 `rejected` 态:pending_review→rejected(编排者,必带 why=结论文件指针,过文件存在门)=打回已登记;rejected→doing(编排者,必带 assignee)=返工派工。两次流转都是编排者动作——打回裁决与返工派工解耦,路由权/限流权不旁落。
2. rejected 计入 ready(返工派工也是派单,同规则竞争槽位);rejected 非 SATISFYING(不满足下游依赖)。
3. pending_review→doing 直返(打回即返工,跳过泊位)保留——能立刻返工时不强制绕行。

## Consequences

- 正:打回积压成为账本一等可见队列;兜底对账可机械区分「没审」(pending_review 无结论文件)vs「审了没派」(rejected);返工派工时机与 reject 裁决解耦,编排者限流权完整。
- 负:一次打回多一笔账(rejected 登记 + doing 派工);rejected 长期积压 = 返工饥饿的显式信号(需要编排者裁决优先级,不是静默丢失——这是特性不是缺陷)。
