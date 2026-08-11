# 0008. docs/game/ 只放游戏玩法(玩家视角事实),自动化实现归 docs/develop/

- **Status**: accepted
- **Date**: 2026-08-11

## Context

`docs/game/<玩法>/` 原本混放:游戏玩法描述(机制 / 数据 / 画面事实)+ 自动化实现(bot 流程 / 决策日志 / 策略 / 踩坑)。`build-craft.md` L77 甚至明写「`docs/game/gameplay/<play>.md` 写玩法 + bot 流程 + 踩坑」—— 把 bot 流程(自动化)塞进游戏玩法目录。

问题:

1. **混了两种漂移源**:游戏玩法 = 游戏事实(游戏版本更新才改);自动化实现 = 代码(代码改才改)。两者混放 → 更新时不知核对游戏还是核对代码,易漂移。
2. **不懂代码的人读不懂**:`docs/game/` 本该是纯游戏知识(机制 / 规则 / 数据),混了 op 链 / 决策日志 / 策略(要懂代码才懂)→ 非开发者(或换玩法的人)读不通。
3. **和 gameplay-recording 核心原则矛盾**:核心原则(L8-15)讲「玩法是客观事实、不是代码附属、玩家视角记非代码视角」—— 但落点(L84)没显式边界,实操把自动化堆进 `docs/game/`(违背原则)。

用户原则(2026-08-11):`docs/game/` 只放游戏玩法(与自动化无关);自动化实现归别处。

## Decision Drivers

- **单一漂移源**:一个文档只跟一种漂移源(游戏版本 or 代码),更新时核对对象明确。
- **可读性**:`docs/game/` 该是纯游戏知识,不懂代码也能读。
- **呼应核心原则**:gameplay-recording L8-15 已讲玩法 = 客观事实,边界是其落点推论(只是没显式化)。

## Considered Options

1. **保持混放(全堆 docs/game/ 方便)**:混漂移源 + 难读 + 违背核心原则(否)。
2. **docs/game/ 只放游戏玩法,自动化归 docs/develop/<玩法>/(选中)**:分离游戏事实 vs 自动化实现,各自漂移源清晰,docs/game/ 纯游戏知识。
3. **自动化实现全归本地 .debug/(不入 git)**:决策日志 / 策略该团队共享(入 git),不能只本地(否,进度 / 临时调研才本地)。

## Decision

选 2。

- **gameplay-recording.md L84** 加内容边界:`docs/game/<玩法>/` 只放游戏玩法本身(玩家视角事实:机制 / 流程 / 数据 / 状态 / 边界,游戏版本更新才改,与自动化代码无关);自动化实现(bot 流程 / 决策日志 / 策略 / 踩坑)归 `docs/develop/<玩法>/`;进度 / 临时调研归本地 `.debug/`。判据:「游戏改了它变,还是代码改了它变?」前者 → `docs/game/`;后者 → `docs/develop/`。
- **build-craft.md L77** 修冲突:玩法归 `docs/game/gameplay/<play>.md`;bot 流程 + 踩坑归 `docs/develop/<play>/`。

## Consequences

- **正向**:`docs/game/` 纯游戏知识(不懂代码能读);漂移源单一(游戏版本 or 代码,不混);和核心原则一致。
- **负向**:现有玩法(如 CW)的 `docs/game/` 里堆了自动化内容(decisions.md / strategy/ / bot 流程)需搬移到 `docs/develop/` —— 这是各项目侧整理(本 ADR 只立规范,不搬项目文件)。
- **边界**:画面事实(screen doc)算游戏玩法(画面是游戏提供的)→ 仍在 `docs/game/screens/`;op 链 / 编排(自动化)→ `docs/develop/`。

## Links

- gameplay-recording.md L84 内容边界 + L8-15 核心原则(玩法 = 客观事实)。
- build-craft.md L77(修冲突)。
