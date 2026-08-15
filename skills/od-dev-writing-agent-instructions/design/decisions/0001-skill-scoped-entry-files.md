# 0001 · 建 skill 管 always-on 入口文件(与 writing-skills 分开)

- **Status**: accepted
- **Date**: 2026-08-16

## Context
用户要一个「编写 AGENTS.md 这类 agent instruction files 的指导 skill」。调研:agents.md 开放标准(格式)成熟但不管内容;Anthropic 官方 memory 文档有加/删判据但散;社区只有模板/对比文。SR 项目 harness 已有相当系统的 context_layering / entry_files 实践(四档分层 / 删了会出错自检 / 两层模式),但锁在项目 docs,换项目即丢。

## Decision Drivers
1. 入口文件与 skill 是不同 artifact,token 经济完全相反(常驻 vs 按需),判据不能混。
2. 判据要跨项目通用(公共仓定位)。
3. 不与 writing-skills 双源。

## Considered Options

| 方案 | 结论 | 理由 |
|---|---|---|
| 并入 od-dev-writing-skills 加一节 | 否决 | 对象不同(skill vs 入口文件),核心动作相反(展开 vs 砍);并入会把两组判据搅在一起,且触发场景不同(写 skill vs 写 AGENTS.md) |
| 独立 skill(采纳) | 采纳 | 独立 artifact 独立 skill;判据互通处显式引用 writing-skills(如干净读者原则 §1.9)不复制 |
| 只留项目 docs 不建 skill | 否决 | 判据通用且 SR/ZZZ 每项目都要写入口文件;docs 不被 agent 按需触发,等于没有 |

## Decision
新建 od-dev-writing-agent-instructions:checklist(判层→判层内归属→写→纯度→流程)+ §1 格式变体地图 / §2 内容取舍(砍为默认 + 四档分层 + 加删节奏)/ §3 共享 vs .local 两层 / §4 反模式。内容来源:agents.md 标准 + Anthropic 官方 + SR context_layering/entry_files 泛化(去项目专属)。

## Consequences
- SR 项目侧 context_layering/entry_files 保留项目专属细节并后续加指针指向本 skill(防双源,由项目侧做)。
- 跨项目(如 ZZZ)写入口文件时可直接用。
- 工具机制细节不进 skill(易变),指向项目对比文档。
