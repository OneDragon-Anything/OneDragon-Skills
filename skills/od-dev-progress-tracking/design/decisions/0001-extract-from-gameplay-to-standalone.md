# ADR-0001: 从 gameplay-automation 提取为独立 skill

## Status

Accepted (2026-08-09)

## Context

进度记录方法论(任务树状态机)原位于 `od-dev-gameplay-automation/references/progress-tracking.md`。

问题:
1. **不可发现**:埋在 gameplay-automation 的 reference 里,只有做 gameplay 时才可能读到。description 不提进度记录 → 触发时不会注意到有这个方法。
2. **作用域过窄**:任务树状态机是**全局规则**(任何复杂多步骤开发都该用),不是 gameplay 专属。
3. **循环依赖**:screen-onboarding 的进度模板反向引用 gameplay-automation/references/progress-tracking.md(gameplay 引 screen-onboarding,screen-onboarding 引 gameplay 的 reference → 不干净)。
4. **实际后果**:智能体在货币战争自动化项目中做了 ~40 轮,从未按方法论组织进度(进度记录变成了线性流水 log,而非任务树状态机),导致撞墙(角色身份感知缺失未被发现、deploy/equip 反复返工)。

## Considered Options

### A. 保持现状(留 gameplay-automation/references/)

- ✗ 不可发现(核心问题)。
- ✗ 作用域过窄。
- ✗ 循环依赖。

### B. 提取为独立 skill

- ✓ 全局可发现(自己的 description 触发)。
- ✓ 作用域正确(全局方法)。
- ✓ 无循环依赖(其他 skill 引用本 skill)。
- − 需更新 gameplay-automation + screen-onboarding 的引用。
- − gameplay 专属的分纲(§10,5 阶段骨架)需留在 gameplay-automation。

### C. 放进一个通用的 "od-dev-fundamentals" skill

- ✓ 全局可用。
- ✗ "fundamentals" 范围模糊(什么算 fundamental?),容易膨胀。
- ✗ 进度记录与其他 fundamentals(如代码规范、Git 约定)关注点不同,混在一起违反单一职责。

## Decision

选 B:提取为独立 skill `od-dev-progress-tracking`。

- SKILL.md = 通用方法(§1-9 总纲 + §10 叶子映射 + §11 事件长尾)。
- gameplay-automation 保留 §10 分纲(5 阶段骨架)在 reference 里,引用本 skill。
- screen-onboarding 引用本 skill(不再反向引用 gameplay)。

## Consequences

- **正面**:
  - 全局可发现 + 可触发(任何复杂多步骤任务)。
  - 其他 skill 干净引用(无循环依赖)。
  - 每个工件 skill 保持自己的进度模板(不 piled together)。
- **负面**:
  - gameplay-automation 的 references/progress-tracking.md 需标注"已提取,见 od-dev-progress-tracking"(或删除通用部分,只留 §10 分纲)。
  - 需更新引用(gameplay-automation SKILL.md line 27 + screen-onboarding SKILL.md line 220)。
