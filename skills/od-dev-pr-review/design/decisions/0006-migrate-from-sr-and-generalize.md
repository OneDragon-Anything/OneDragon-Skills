# 0006. 自 SR 仓迁入公共仓 + 泛化项目专属引用

- **Status**: accepted
- **Date**: 2026-08-15

## Context

本 skill 诞生于 SR 仓(`sr-od-dev-pr-review`),方法论骨架(L0~L4 分级 / 集成基线纪律 / 框架语义必查项 / 冲突解决)与「框架语义必查项」(`op_callback` 双触发 / `round_wait` 重置重试预算 / `execute()` 重入 / `node_from` 路由)均为 OneDragon 框架级,ZZZ 等姊妹项目同样适用;组织内 PR 流程(CodeRabbit / 主仓+测试仓配对)同构。原文含 SR 专属引用:测试仓目录名(`sr-od-test`)×3、`daemon`、SR MCP 工具名(`click_game` 等)、SR doc 路径(`docs/game/*`)、`superpowers:receiving-code-review` 外部指针。

## Decision Drivers

- **框架级通用**:审查判据锚定 `one_dragon` 框架语义,跨项目成立。
- **自包含**(规范 3 硬门):公共仓不引引用闭包外的 skill / 路径。
- **泛化约束**:公共 skill 不提项目专属基础设施。

## Considered Options

1. **留 SR 仓**:ZZZ 等项目用不上;框架语义必查项是系列级资产。
2. **迁入原样保留**:SR 专属引用在别的项目是死链 / 空指针。
3. **迁入 + 泛化**(选中):专属引用按映射泛化;框架地基级接口名(`@operation_node` / `round_by_*` / `op_callback` …)按规范 3 保留全名。
4. **公共仓重写**:方法论经 30 个 open PR 实操提炼,重写无增益。

## Decision

选 3。泛化映射:

- `git -C sr-od-test` → `git -C <测试仓目录>`(测试仓配对模式是系列约定,保留)。
- SR MCP 工具名(`click_game` / `capture_game_screen` / `analyze_screen` / `run_operation` / `run_standalone_app` / `get_run_status` / `pc_alt`)→ 通用说法(「MCP 点击 / 截图 / 画面分析 / 运行 op / app / 状态查询工具」+「工具名按所在项目 MCP server 约定」);`经 daemon 重启 server` → `重启 MCP server(按所在项目机制)`。
- SR doc 路径(`docs/game/gameplay/` / `docs/game/screens/` / `assets/game_data/screen_info/`)→ 「项目的玩法 doc / 画面建档 doc / 画面模型(screen_info)」。
- `sr-od-dev-pr-finishing` → `od-dev-pr-finishing`(同步迁入);`superpowers:receiving-code-review` → 指向 pr-finishing 流程 2(其核心已内联)。

## Consequences

- **正向**:系列项目共享同一套 PR 审查方法论;框架语义必查项跨项目防错。
- **负向**:L4 live 的 MCP 操作从「点名工具」变「按约定泛指」,单项目内执行时需一步心译;GREEN 状态仍 draft(随迁不变)。
- **follow-up**:各项目若有 MCP 工具名速查,放项目自己的 doc,不进本 skill。

## Links

- 同批:[pr-finishing ADR-0004](../../od-dev-pr-finishing/design/decisions/0004-migrate-from-sr-and-drop-superpowers.md)。
- 泛化先例:[deciding-a-fix ADR-0003](../../od-dev-deciding-a-fix/design/decisions/0003-migrate-from-sr-and-drop-superpowers.md)。
