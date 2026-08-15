# 0004. 自 SR 仓迁入公共仓 + 去 superpowers 外部指针

- **Status**: accepted
- **Date**: 2026-08-15

## Context

本 skill 诞生于 SR 仓(`sr-od-dev-pr-finishing`),内容为 GitHub + CodeRabbit 工作流(done criteria / GraphQL resolve / CodeRabbit 平台行为陷阱 / 跨仓 PR 协同),专属词扫描零 SR 命中——天然通用,OneDragon 系列项目统一采用 CodeRabbit、主仓+测试仓配对模式同构。原文 3 处 `superpowers:*` 外部指针(receiving-code-review ×2 / finishing-a-development-branch ×1),与公共仓自包含立场冲突。

## Decision Drivers

- **零泛化成本**:正文本就无项目专属引用,迁移即通用。
- **自包含**(规范 3 硬门)。
- **单条评论方法已半内联**:流程 2 原文已含「verify → 评估 → 决定 + 两条出路」,去指针只需把方法展开写全。

## Considered Options

1. **留 SR 仓**:系列项目重复摸索 CodeRabbit 平台陷阱。
2. **迁入原样保留 superpowers 指针**:破坏自包含。
3. **迁入 + 指针内联化**(选中):receiving-code-review 核心展开进流程 2;分支收尾决定(merge/PR/discard)改「由维护者 / 所在环境流程决定」。
4. **重写**:踩坑论据(replies 端点 / ack comment 编辑复用 / auto-pause vs rate-limit)是实操沉淀,重写丢证据链。

## Decision

选 3:

- 迁入 `skills/od-dev-pr-finishing/`;ADR-0001~0003(CodeRabbit 写死 / 双 API / 状态判据)原样迁入,决策不变。
- 流程 2 自含单条方法:「verify → 评估 → 决定」展开 + 两条出路;description / 边界同步去指针。
- 「本项目跨仓」→「OneDragon 系列项目常跨仓」(配对模式系列通用)。
- CodeRabbit 写死不变(ADR-0001:系列项目统一采用;抽象成 review-bot 接口会稀释平台陷阱细节的价值)。

## Consequences

- **正向**:系列项目共享收尾流程;CodeRabbit 平台陷阱知识单源;skill 完全自包含。
- **负向**:CodeRabbit 行为变化需人工跟进维护(半衰期短的活文档,ADR-0001 已接受此权衡);GREEN 仍 draft。
- **follow-up**:CodeRabbit 行为变更时更新 SKILL.md + 补 ADR(平台行为驱动的判据,见 ADR-0003)。

## Links

- 同批:[pr-review ADR-0006](../../od-dev-pr-review/design/decisions/0006-migrate-from-sr-and-generalize.md)。
- 同源去 superpowers:[write-operation ADR-0010](../../od-dev-write-operation/design/decisions/0010-inline-debugging-discipline-drop-superpowers-pointer.md)。
