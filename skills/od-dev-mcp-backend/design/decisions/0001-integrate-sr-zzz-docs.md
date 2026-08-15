# 0001. 整合 SR / ZZZ 双源 backend 文档为公共 skill(以 SR 为基底 + 并入 ZZZ 受众演进)

- **Status**: accepted
- **Date**: 2026-08-15

## Context

SR(`docs/develop/sr_od/backend/`)与 ZZZ(`docs/develop/zzz/backend/`)各持一套 backend 文档,文件名一一对应。实测对比(2026-08-15):

- **README**:逐字镜像(仅项目名 / 端口 / screen-recognizers 行差异)。
- **design-principles**(P1-P14):同构;**ZZZ 独有**「两类受众(①读源码 / ②远程源码盲)+ P1 源码盲例外 + P9 docstring 透传约定 + 总表受众分列」;**SR 独有**「P2 引 per-screen recognizer」。
- **mcp-implementation**:两边各 105 行,`Compare-Object` 仅 4 行差异且全是项目名 —— 实质 100% 同构。
- **screen-recognizers.md**:SR 独有(ZZZ 无此文件);契约在公共包 `one_dragon/base/screen/screen_recognizer.py`,机制系列通用。

同步成本已在发生:SR 侧开专门分支做「同步 ZZZ backend 演进」。用户问「哪个更好 / 还是整合」。

## Decision Drivers

- **双源必漂移**:同构内容两处维护,已出现各自演进(受众块 vs recognizer)。
- **方法论 vs 实例可分**:设计原则 / 实现规范 / recognizer 机制是方法论(系列通用);类名 / 工具表 / 端口是项目实例(各仓 spec)。
- **泛化约束**:公共 skill 不提项目专属基础设施。

## Considered Options

1. **选 ZZZ 做基底**:ZZZ 有受众块但缺 recognizer 演进;且 SR 侧文档体量与近期演进(active 到 08-14)更全。
2. **选 SR 做基底原样迁**:丢 ZZZ 受众块(该块对「远程 MCP 纯使用者」场景是关键演进)。
3. **SR 基底 + 并入 ZZZ 受众块(选中)**:SR 是超集演进(recognizer + 对应原则引用),ZZZ 受众块是独立成熟增量,并入即得全集。
4. **重写提炼**:文档已高度凝练(踩坑校准过的判据密度),重写无增益且丢实战细节。

## Decision

选 3:

- `references/design-principles.md` = SR 全文 + ZZZ 四处受众增量(适用前提 / P1 例外 / P9 约定 / 总表行),泛化项目名。
- `references/implementation.md` = SR 版泛化(项目路径 / 测试仓 / daemon 措辞)。
- `references/screen-recognizers.md` = SR 版泛化(项目实例抽象化;删 gitignored 设计 spec 引用;并发安全论据保留模式去项目名)。
- SKILL.md 只放核心心智(能力边界两问 + 受众分层)+ 判定主线 + checklist;细则全在 references(progressive disclosure)。

## Consequences

- **正向**:设计方法论单源,两仓(及后续项目)新 tool 开发同一准绳;ZZZ 引入 recognizer 机制时直接有指导;受众②场景(远程纯使用者)的语义透传约定进入公共层。
- **负向**:各仓 design-principles / mcp-implementation / screen-recognizers 需另行删除瘦身(follow-up,等 SR 的 sync 分支合并后做,避免与进行中工作打架);GREEN 待做。
- **follow-up**:① SR/ZZZ 各仓瘦身(overview「各仓瘦身」节列了保留 / 删除清单);② 下次新增 tool 时 GREEN 验证;③ 官方 mcp-server-dev tool-design 引用保留为「有则更好」,非硬依赖。

## Links

- 源:SR `docs/develop/sr_od/backend/`(design-principles / mcp-implementation / screen-recognizers)、ZZZ `docs/develop/zzz/backend/`(受众块增量)。
- 泛化先例:[pr-review ADR-0006](../../od-dev-pr-review/design/decisions/0006-migrate-from-sr-and-generalize.md)。
