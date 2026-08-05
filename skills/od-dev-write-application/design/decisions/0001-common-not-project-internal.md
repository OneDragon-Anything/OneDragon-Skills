# 0001. app skill 为 common(推翻 write-operation ADR-0001 的"项目内")

- **Status**: accepted
- **Date**: 2026-08-05
- **Supersedes**: write-operation ADR-0001 中「application skill(项目内,待建)」的定位

## Context

write-operation [ADR-0001](../../od-dev-write-operation/design/decisions/0001-split-by-granularity.md)(按粒度拆 op/app/玩法三层)把 app skill 标为「项目内,待建」。当时的考虑:app 产品化(factory/config/GUI)看似项目特定。

调研发现:app 方法论的根基 —— `Application` / `ApplicationFactory` / `AppRunRecord` / `YamlConfig` / 自动发现机制 —— **全在 `one_dragon` 公共包**(SR / ZZZ 共享)。项目特有的只是特化子类(各项目的 `XxxApplication`)+ 个别收尾 op(回 hub 的 op),这些是泛化点(见 od-dev-writing-skills §3.6),不是「项目内」的理由。ZZZ 已有 `zzz-od-dev-plugin` 同类 skill,印证方法论跨项目通用。

## Decision Drivers

- **单源 / 跨项目复用**:SR + ZZZ 都写 app,方法论该共享(与 write-operation 一致)。
- **泛化可行**:框架级 API 是公共包(in-circle);项目特化子类 / 收尾 op / hub 画面可泛化为通用说法。

## Considered Options

1. **项目内**(各项目自己写 app skill):双源,SR / ZZZ 各写一遍,会漂移;ZZZ 已有的 `zzz-od-dev-plugin` 经验无法直接复用给 SR。
2. **common**(`od-dev-write-application`,项目特化泛化):单源,跨项目复用(选中)。

## Decision

选 **2**。app skill = common `od-dev-write-application`。项目特化(各项目的 `XxxApplication` 子类 / 回 hub 的收尾 op / 最通用的 hub 画面 / `src/<project>/` 路径)泛化为「项目的 Application 子类 / 回 hub 的收尾 op / 最通用的画面 / `src/<project>/`」(见 SKILL.md,符 §3.6)。

## Consequences

- **正向**:SR / ZZZ 共享一套 app 方法论;与 write-operation(也 common)粒度对齐;ZZZ `zzz-od-dev-plugin` 的成熟内容可直接参考。
- **负向**:ZZZ 的 `zzz-od-dev-plugin` + SR 的"待建"引用需迁移指向 common(后续同步工作)。
- **follow-up**:迁移 ZZZ `zzz-od-dev-plugin` + SR 引用 → common(像其他已迁的 skill 一样)。

## Links

- 推翻:write-operation [ADR-0001](../../od-dev-write-operation/design/decisions/0001-split-by-granularity.md) 的「application skill 项目内」定位(本 ADR 把它改为 common)。
- 参考:ZZZ `zzz-od-dev-plugin` skill(同类,内容作参考来源)。
