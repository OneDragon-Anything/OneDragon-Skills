# 0010. 通用调试纪律内联,去 superpowers:systematic-debugging 外部指针

- **Status**: accepted
- **Date**: 2026-08-15

## Context

SKILL.md 边界节原有指针:「通用 bug 定位 / 修复流程 → `superpowers:systematic-debugging` / deciding-a-fix skill(项目内)」—— 迁移自 SR 仓(SR 环境 superpowers 是标配),是当时环境的产物。问题:

1. **公共仓消费者异构**:本仓给所有 OneDragon 项目 / 各 AI 工具用,superpowers 不在本仓引用闭包内(规范 3:引用闭包外的状态 = 在别人机器上不存在)。未安装时该指针按普通文本读,指向空。
2. **实际含量极小**:对照本 skill 已有内容(读日志先行 / 多样本核实 / 预料外调研建档 / 信息密度),systematic-debugging 额外提供的只有三条通用纪律(改前假设先行 / 一次只改一个变量 / 修根因不修症状),约三行字。
3. **「先可靠复现」环节水土不服**:游戏有状态,op 的复现手段是截图 fixture(本 skill testing.md 已覆盖),不是它的复现循环。

## Decision Drivers

- **自包含**(规范 3 硬门:引用 target 必须在已提交仓库里)。
- **不随外部 skill 可用性漂移**(与 writing-skills ADR-0005 同款理由)。
- **调试本就在范围内**(skill 定位 = 写 / 改 / 调试单个 Operation,内联不扩围)。

## Considered Options

1. **保留外部指针**:公共仓引用闭包外 skill,未安装的消费者拿到空指针。
2. **内联三条纪律 + 删指针**(选中):实际缺口只有三行,内联成本最低;边界行改指项目内调试类 skill(如有)。
3. **整合完整调试方法论一节**:超出实际缺口(其余内容本 skill 已有),冗余。

## Decision

选 2:

- 三条通用调试纪律(改前形成假设 / 一次只改一个变量 / 修根因不修症状)内联:SKILL.md 必守不变量 #2 补 compact 版;`references/runtime-craft.md`「调试纪律」补完整版(单源展开,SKILL.md 指向它)。
- 边界节删 superpowers / 项目内 skill 具名指针,泛化为「所在项目的调试类 skill(如有)」。
- 本仓从此**零外部 skill 功能依赖**。

## Consequences

- **正向**:公共仓完全自包含,消费者无需安装任何外部 skill;调试纪律在 op 语境内表述,比通用指针更贴。
- **负向**:通用调试方法论的完整展开不在本仓 —— 项目需要更全的可自建项目级调试 skill(SR 已有),或未来再评估是否升公共 skill。
- **follow-up**:writing-skills 中的 superpowers 提及(出处署名 / 格式示例 / 刻意偏离声明,见其 ADR-0005/0006)保留 —— 那是方法论出处记录,非功能依赖。

## Links

- SKILL.md 必守不变量 #2 + 边界节;`references/runtime-craft.md` 调试纪律。
- 同源:[ADR-0005](../../../od-dev-writing-skills/design/decisions/0005-drop-superpowers-dependency.md)(writing-skills 去 superpowers 依赖)。
