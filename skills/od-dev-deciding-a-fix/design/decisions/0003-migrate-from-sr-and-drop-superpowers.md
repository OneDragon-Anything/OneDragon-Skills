# 0003. 自 SR 仓迁入公共仓 + 去 superpowers 外部指针

- **Status**: accepted
- **Date**: 2026-08-15

## Context

本 skill 诞生于 SR 仓(`sr-od-dev-deciding-a-fix`),内容为五步通用修复决策框架(RCA / Impact Analysis / Trade-off Matrix / Hypothesis-driven Verify),零项目专属基础设施。公共仓侧已有两处等待它:`od-dev-writing-skills` 引 `od-dev-deciding-a-fix` 作方法论型范例(原为落空引用);`od-dev-write-operation` 边界需要「定位后怎么修」的去处(ADR-0010 刚把 superpowers 指针泛化)。原 SKILL.md 有 4 处 `superpowers:systematic-debugging` / `superpowers:brainstorming` 外部指针(SR 环境标配的产物),与公共仓自包含立场冲突(同 write-operation ADR-0010、writing-skills ADR-0005)。

## Decision Drivers

- **泛化成立**:内容全为业界方法论,框架级概念(op 陌生画面)对 OneDragon 系列通用。
- **引用闭环**:公共仓已有引用等着这个名字;SR 侧 debug-automation 的分工(通用决策 vs 项目排查判据)因迁入更干净。
- **自包含**(规范 3 硬门):公共仓不引引用闭包外的 skill。

## Considered Options

1. **留在 SR 仓**:公共仓 writing-skills 范例引用继续落空;ZZZ 等项目用不上。
2. **迁入公共仓,superpowers 指针原样保留**:破坏自包含,未安装 superpowers 的消费者拿到空指针。
3. **迁入 + 指针适配**(选中):`systematic-debugging` → 通用调试纪律(`od-dev-write-operation`,ADR-0010 刚内联的三条)+「所在项目调试类 skill」;`brainstorming` → 泛化措辞「需求设计流程」。
4. **在公共仓重写整个 skill**:内容已成熟(含 baseline 沉淀的两个必填槽位),重写无增益。

## Decision

选 3:

- 迁入 `skills/od-dev-deciding-a-fix/`,frontmatter name 同步改;ADR-0001/0002 原样迁入(历史决策记录,不可变)。
- superpowers 指针按上述映射适配;`od-dev-screen-onboarding` 引用本就是公共仓名,不变。
- SR 仓删源目录,debug-automation 等引用改指 `od-dev-deciding-a-fix`,junction 重指公共仓(SR 侧改动不随本 commit)。

## Consequences

- **正向**:公共仓 9 个 skill;writing-skills 范例引用闭环;write-operation 边界可指名;SR 侧 debug-automation 专注项目专属判据。
- **负向**:SKILL.md 状态仍是 draft(GREEN-pending),迁入不改变验证状态;GREEN utility test 待跑。
- **follow-up**:跑 GREEN(见 overview「当前状态」);SR 侧引用 / junction / 文档同步。

## Links

- 同源去 superpowers:[write-operation ADR-0010](../../../od-dev-write-operation/design/decisions/0010-inline-debugging-discipline-drop-superpowers-pointer.md)、[writing-skills ADR-0005](../../../od-dev-writing-skills/design/decisions/0005-drop-superpowers-dependency.md)。
- SKILL.md「不适用」/ 步骤 0;overview「落点」「自身一致性」。
