# 0002. hub 编排必做 + resume 加分(非常规默认)

- **Status**: accepted
- **Date**: 2026-08-05

## Context

app 编排(节点图)有两种稳健性档位:

1. **hub 模式**:app 第一个 op 返回最通用的画面(hub)→ 从 hub 跑流程 → 最后一个 op 返回 hub。已知起止态 + 一条龙里 app 间在 hub 干净衔接。
2. **resume 模式**:入口 op 先自检当前态、已在玩法就 skip → crash / 重启 / 手动接管后能从任何态 resume。

resume 更鲁棒但更复杂(每个入口 op 要自检当前态);hub 够日常自动化且简单。现有 app 多数用 hub 模式;少数长流程 app 加了 resume 增强。

## Decision Drivers

- **够用即可**:日常自动化(一条龙批量跑)只需 hub 模式(已知起止 + 衔接)。
- **简单优先**:hub 作默认;resume 是超出日常需求的增强。
- **一条龙衔接契约**:app 都在 hub 交接(上一个回 hub = 下一个起点)。

## Considered Options

1. **resume 作默认(要求所有 app)**:过严 —— 日常自动化用不上,徒增每个入口 op 的自检负担。
2. **hub 作默认 + resume 加分**(选中):够用 + 简单;长流程 / 易崩的 app 才加 resume。
3. **只 hub 不要 resume**:过死 —— resume 对某些 app(长肉鸽 / 自走棋类)有真实价值。

## Decision

选 **2**。**hub 模式必做**(第一个 op 回 hub + 最后一个 op 回 hub);**resume 加分**(非必做;长流程 / 易崩 / 用户常中途接管的 app 才加)。

## Consequences

- **正向**:日常自动化简单够用;app 间 hub 衔接干净;需要 resume 的 app 可按需加。
- **负向**:没有 resume 的 app,crash 后不能从对局中态 resume(得从 hub 重跑)—— 日常自动化可接受。
- **边界**:resume 写法见 SKILL.md(入口 op 自检当前态 + skip);hub 是默认。

## Links

- SKILL.md「app 编排:hub 模式(必做)+ resume(加分)」。
- 现有 app 多为 hub 模式;少数长流程 app(自走棋 / 肉鸽类)用 resume 增强。
